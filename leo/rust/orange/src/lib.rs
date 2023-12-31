//@+leo-ver=5-thin
//@+node:ekr.20231226052346.1: * @file ../rust/orange/src/lib.rs
//! This is the `orange` binary.

//@+<< use: orange/src/lib.rs >>
//@+node:ekr.20231230105848.1: ** << use: orange/src/lib.rs >>
// use std::fmt::Debug;
use std::process::ExitCode;
use rustpython_parser::{lexer::lex, Mode, parse_tokens};

// use rustpython_parser::ast::Ast;
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
    

    if false {
        print_tokens(python_source);
    }
    
    // print ast.
    if false {
        //print_ast(ast);
    }
    
    if true {
        // ast: enum Result
        match ast {
            Ok(tree) => {
                println!("\nTree:");
                // tree:  enum `rustpython_parser::rustpython_ast::Mod`
                if true {  // Experimental.
                    // let tree_iter = tree.iter();
                    // for z in tree.traverse() {
                    for z in tree.visitor() {
                        println!("{:#?}", z);
                    }
                }
                else {
                    println!("{:#?}", tree);
                }
            },
            Err(_) => println!("no ast"),
        }
    }

    println!("orange/src/lib.rs: done!");
    ExitCode::SUCCESS
}
//@+node:ekr.20231230114358.1: *3* fn: print_ast (not used)
// fn print_ast(ast: Result<Ast, &'static str>) {
    // match ast {
        // Ok(tree) => {
            // println!("\nTree:");
            // println!("{:#?}", tree);
        // },
        // Err(_) => println!("no ast"),
    // }
// }

//@@language rust
//@+node:ekr.20231230113914.1: *3* fn: print_tokens
// https://docs.rs/rustpython-parser/latest/rustpython_parser/lexer/index.html#example

fn print_tokens(python_source: &str) {

    // Can't be formatted with `{:?}` because it doesn't implement `Debug`.
    let tokens = lex(python_source, Mode::Module)
        .map(|tok| tok.expect("Failed to lex"))
        .collect::<Vec<_>>();

    println!("\nTokens:");
    for (token, range) in tokens {
        println!("  {token:?}@{range:?}");
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
