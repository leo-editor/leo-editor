//@+leo-ver=5-thin
//@+node:ekr.20231226052346.1: * @file ../rust/orange/src/lib.rs
//! This is the `orange` binary.

//@+<< use: orange/src/lib.rs >>
//@+node:ekr.20231230105848.1: ** << use: orange/src/lib.rs >>
// use std::fmt::Debug;
use std::process::ExitCode;
use rustpython_parser::{lexer::lex, Mode, parse_tokens};

//@-<< use: orange/src/lib.rs >>

//@+others
//@+node:ekr.20231230104754.1: ** fn: run & helpers
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
    
    // https://docs.rs/rustpython-parser/latest/rustpython_parser/lexer/index.html#example
    print_tokens(python_source);

    if false { // print ast.
        match ast {
            Ok(tree) => {
                println!("\nTree:");
                println!("{:#?}", tree);
            },
            Err(_) => println!("no ast"),
        }
    }

    println!("orange/src/lib.rs: done!");
    ExitCode::SUCCESS
}
//@+node:ekr.20231230113914.1: *3* fn: print_tokens
fn print_tokens(python_source: &str) {

    // Can't be formatted with `{:?}` because it doesn't implement `Debug`.
    let debug_tokens = lex(python_source, Mode::Module)
        .map(|tok| tok.expect("Failed to lex"))
        .collect::<Vec<_>>();
    println!("\nTokens:");
    for (debug_token, range) in debug_tokens {
        println!("  {debug_token:?}@{range:?}");
    }
}

//@@language rust
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
