//@+leo-ver=5-thin
//@+node:ekr.20231226052346.1: * @file ../rust/orange/src/lib.rs
//! This is the `orange` binary.

use std::process::ExitCode;

pub fn run() -> ExitCode {
    // The main line for orange.
    println!("orange/src/lib.rs: run");
    
    ExitCode::SUCCESS
}

//@+others
//@+node:ekr.20231226041203.1: ** mod tests
#[cfg(test)]
mod tests {
    //@+others
    //@+node:ekr.20231223154842.1: *3* fn: test_driver
    #[test]
    fn test_driver() {
        println!("driver test")
        // assert_eq!(2 + 2, 4);
    }
    //@-others
}
//@-others
//@-leo
