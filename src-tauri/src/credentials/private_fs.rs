#[cfg(windows)]
#[path = "private_fs_windows.rs"]
mod windows;

#[cfg(windows)]
pub use windows::{check, directory, open, Lock};

#[cfg(not(windows))]
use std::{
    fs::{self, File, OpenOptions},
    path::Path,
};

#[cfg(unix)]
use std::os::{
    fd::AsRawFd,
    unix::fs::{MetadataExt, OpenOptionsExt},
};

#[cfg(not(windows))]
pub fn check(path: &Path, directory: bool) -> Result<(), String> {
    let metadata =
        fs::symlink_metadata(path).map_err(|_| "Cannot inspect credential file permissions")?;
    if metadata.file_type().is_symlink()
        || metadata.is_dir() != directory
        || (!directory && !metadata.is_file())
    {
        return Err(
            "Credential path must be a regular file or private directory, never a symlink".into(),
        );
    }
    #[cfg(unix)]
    {
        if metadata.uid() != unsafe { libc::geteuid() }
            || metadata.mode() & 0o777 != if directory { 0o700 } else { 0o600 }
            || (!directory && metadata.nlink() != 1)
        {
            return Err("Credential files require user-only permissions and ownership".into());
        }
    }
    #[cfg(not(unix))]
    return Err(
        "Local credential storage requires verified native file permissions on this platform"
            .into(),
    );
    #[allow(unreachable_code)]
    Ok(())
}

#[cfg(not(windows))]
pub fn directory(path: &Path) -> Result<(), String> {
    if !path
        .try_exists()
        .map_err(|_| "Cannot inspect credential directory")?
    {
        #[cfg(unix)]
        {
            use std::os::unix::fs::DirBuilderExt;
            let result = fs::DirBuilder::new().mode(0o700).create(path);
            if let Err(error) = result {
                if error.kind() != std::io::ErrorKind::AlreadyExists {
                    return Err("Cannot create private credential directory".into());
                }
            }
        }
        #[cfg(not(unix))]
        return Err(
            "Local credential storage requires verified native file permissions on this platform"
                .into(),
        );
    }
    check(path, true)
}

#[cfg(not(windows))]
pub fn open(path: &Path, create: bool) -> Result<File, String> {
    let mut options = OpenOptions::new();
    options.read(true).write(true);
    if create {
        options.create_new(true);
    }
    #[cfg(unix)]
    options
        .mode(0o600)
        .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC);
    let file = options
        .open(path)
        .map_err(|_| "Cannot open private credential file")?;
    check(path, false)?;
    #[cfg(unix)]
    {
        let metadata = file
            .metadata()
            .map_err(|_| "Cannot inspect credential file")?;
        if metadata.uid() != unsafe { libc::geteuid() }
            || metadata.mode() & 0o777 != 0o600
            || metadata.nlink() != 1
        {
            return Err("Credential file permissions changed".into());
        }
    }
    Ok(file)
}

#[cfg(not(windows))]
pub struct Lock(File);
#[cfg(not(windows))]
impl Lock {
    pub fn acquire(path: &Path) -> Result<Self, String> {
        // The only shared coordination file contains no secrets.
        let file = match open(path, true) {
            Ok(file) => file,
            Err(_) if path.exists() => open(path, false)?,
            Err(error) => return Err(error),
        };
        #[cfg(unix)]
        if unsafe { libc::flock(file.as_raw_fd(), libc::LOCK_EX) } != 0 {
            return Err("Cannot lock credential storage".into());
        }
        Ok(Self(file))
    }
}
#[cfg(not(windows))]
impl Drop for Lock {
    fn drop(&mut self) {
        #[cfg(unix)]
        unsafe {
            libc::flock(self.0.as_raw_fd(), libc::LOCK_UN);
        }
    }
}
