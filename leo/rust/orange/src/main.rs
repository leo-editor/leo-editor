
use std::process::ExitCode;

pub fn main() -> std::process::ExitCode {
    // Run the orange binary.

    // println!("orange/src/main.rs: calling orange::run");
    
    orange::run();

    return ExitCode::SUCCESS;
}
