//! Compensate an opt-in OS credential write when public metadata cannot commit.
//! This is tested with fake stores; no unit test opens the user's keychain.
use super::SaveError;

pub fn commit<T>(
    write: impl FnOnce() -> Result<(), String>,
    persist: impl FnOnce() -> Result<T, String>,
    recover: impl FnOnce() -> Result<(), String>,
) -> Result<T, SaveError> {
    let result = write().and_then(|()| persist());
    match result {
        Ok(value) => Ok(value),
        Err(_) => match recover() {
            Ok(()) => Err("Could not save API key; the previous OS credential was restored".into()),
            Err(_) => Err(SaveError {
                message: "Could not verify OS credential recovery; re-enter or delete the API key before translating".into(),
                uncertain: true,
            }),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    #[test]
    fn metadata_failure_restores_the_previous_key_and_failed_recovery_is_unknown() {
        for fail_recovery in [false, true] {
            let key = RefCell::new("old-fixture");
            let error = commit(
                || {
                    *key.borrow_mut() = "new-fixture";
                    Ok(())
                },
                || Err::<(), _>("fixture commit failure".into()),
                || {
                    if fail_recovery {
                        Err("fixture recovery failure".into())
                    } else {
                        *key.borrow_mut() = "old-fixture";
                        Ok(())
                    }
                },
            )
            .unwrap_err();
            assert_eq!(error.uncertain, fail_recovery);
            assert_eq!(
                *key.borrow(),
                if fail_recovery {
                    "new-fixture"
                } else {
                    "old-fixture"
                }
            );
        }
    }

    #[test]
    fn failed_write_is_recovered_without_committing_metadata() {
        let persisted = RefCell::new(false);
        let recovered = RefCell::new(false);
        let result = commit(
            || Err("fixture OS write failure".into()),
            || {
                *persisted.borrow_mut() = true;
                Ok(())
            },
            || {
                *recovered.borrow_mut() = true;
                Ok(())
            },
        );
        assert!(!result.unwrap_err().uncertain);
        assert!(!*persisted.borrow());
        assert!(*recovered.borrow());
    }
}
