//! Absolute startup deadlines. Work after the handshake has no blanket timeout.
use std::{future::Future, time::Duration};
use tokio::time::{timeout_at, Instant};

pub const HANDSHAKE_TIMEOUT: &str = "CORE_HANDSHAKE_TIMEOUT";
pub const BOOTSTRAP_TIMEOUT: &str = "BOOTSTRAP_TIMEOUT";

pub struct StartupDeadlines {
    handshake: Instant,
    bootstrap: Option<Instant>,
}

impl StartupDeadlines {
    pub fn new(kind: &str) -> Self {
        Self::with_limits(kind, Duration::from_secs(30), Duration::from_secs(60))
    }

    fn with_limits(kind: &str, handshake: Duration, bootstrap: Duration) -> Self {
        let started = Instant::now();
        Self {
            handshake: started + handshake,
            bootstrap: (kind == "app.bootstrap").then_some(started + bootstrap),
        }
    }

    fn deadline(&self, saw_hello: bool) -> Option<(Instant, &'static str)> {
        if !saw_hello {
            Some((self.handshake, HANDSHAKE_TIMEOUT))
        } else {
            self.bootstrap.map(|deadline| (deadline, BOOTSTRAP_TIMEOUT))
        }
    }

    pub async fn receive<F: Future>(
        &self,
        saw_hello: bool,
        event: F,
    ) -> Result<F::Output, &'static str> {
        match self.deadline(saw_hello) {
            Some((deadline, code)) => {
                // Ready events can otherwise succeed after the timeout. Chatter must
                // not extend either absolute startup deadline.
                if Instant::now() >= deadline {
                    return Err(code);
                }
                timeout_at(deadline, event).await.map_err(|_| code)
            }
            None => Ok(event.await),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn runtime() -> tokio::runtime::Runtime {
        tokio::runtime::Builder::new_current_thread()
            .enable_time()
            .build()
            .unwrap()
    }

    #[test]
    fn no_hello_times_out_for_both_bootstrap_and_write_requests() {
        runtime().block_on(async {
            for kind in ["app.bootstrap", "translate.start", "restore.start"] {
                let deadlines = StartupDeadlines::with_limits(
                    kind,
                    Duration::from_millis(10),
                    Duration::from_millis(30),
                );
                assert_eq!(
                    deadlines.receive(false, std::future::pending::<()>()).await,
                    Err(HANDSHAKE_TIMEOUT)
                );
            }
        });
    }

    #[test]
    fn bootstrap_still_has_a_deadline_after_hello() {
        runtime().block_on(async {
            let deadlines = StartupDeadlines::with_limits(
                "app.bootstrap",
                Duration::from_millis(10),
                Duration::from_millis(20),
            );
            assert_eq!(
                deadlines.receive(false, std::future::ready(())).await,
                Ok(())
            );
            assert_eq!(
                deadlines.receive(true, std::future::pending::<()>()).await,
                Err(BOOTSTRAP_TIMEOUT)
            );
        });
    }

    #[test]
    fn chatter_and_duplicate_hello_do_not_reset_the_deadline() {
        runtime().block_on(async {
            let deadlines = StartupDeadlines::with_limits(
                "app.bootstrap",
                Duration::from_millis(10),
                Duration::from_millis(20),
            );
            tokio::time::sleep(Duration::from_millis(25)).await;
            assert_eq!(
                deadlines.receive(false, std::future::ready(())).await,
                Err(HANDSHAKE_TIMEOUT)
            );
            assert_eq!(
                deadlines.receive(true, std::future::ready(())).await,
                Err(BOOTSTRAP_TIMEOUT)
            );
        });
    }

    #[test]
    fn work_after_hello_is_not_killed_by_the_startup_deadline() {
        runtime().block_on(async {
            for kind in [
                "scan.start",
                "translate.start",
                "translate.resume",
                "restore.start",
            ] {
                let deadlines = StartupDeadlines::with_limits(
                    kind,
                    Duration::from_millis(1),
                    Duration::from_millis(1),
                );
                assert_eq!(
                    deadlines
                        .receive(true, async {
                            tokio::time::sleep(Duration::from_millis(10)).await;
                            42
                        })
                        .await,
                    Ok(42)
                );
            }
        });
    }
}
