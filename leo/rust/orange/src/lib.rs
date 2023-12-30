//@+leo-ver=5-thin
//@+node:ekr.20231226052346.1: * @file ../rust/orange/src/lib.rs
//! This is the `orange` binary.

use std::process::ExitCode;
use rustpython_parser::{lexer::lex, Mode, parse_tokens};

pub fn run() -> ExitCode {
    // The main line for orange.
    println!("orange/src/lib.rs: run");
    
    // https://docs.rs/rustpython-parser/latest/rustpython_parser/#examples

    let python_source = r#"
def is_odd(i):
   return bool(i & 1)
"#;

    let tokens = lex(python_source, Mode::Module);
    let ast = parse_tokens(tokens, Mode::Module, "<embedded>");
    assert!(ast.is_ok());

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
//@@language rust
//@-leo
