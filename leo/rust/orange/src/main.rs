
use rustpython_parser::{lexer::lex, Mode, parse_tokens};
use std::process::ExitCode;

pub fn main() -> std::process::ExitCode {
    // Run the orange binary.
    println!("orange/src/main.rs");
    
    let python_source = r#"
def is_odd(i):
   return bool(i & 1)
"#;

    let tokens = lex(python_source, Mode::Module);
    let ast = parse_tokens(tokens, Mode::Module, "<embedded>");
    assert!(ast.is_ok());

    // orange::run()

    ExitCode::SUCCESS
}


