//@+leo-ver=5-thin
//@+node:ekr.20231226052346.1: * @file ../rust/orange/src/lib.rs
//! This is the `orange` binary.

use std::process::ExitCode;

// use rustpython::
use rustpython_vm as vm;

pub fn run() -> ExitCode {
    // The main line for orange.
    println!("orange/src/lib.rs: run");
    
    if false {
    
        // From RustPython/examples/hello_embed.rs.
        // vm::Interpreter::without_stdlib(Default::default()).enter(|vm| {
            // let scope = vm.new_scope_with_builtins();
            // let source = r#"print("Hello World!")"#;
            // let code_obj = vm
                // .compile(source, vm::compiler::Mode::Exec, "<embedded>".to_owned())
                // // .map_err(|err| vm.new_syntax_error(&err, Some(source)))?;
                // .map_err(|err| vm.new_syntax_error(&err, Some(source)));

            // // vm.run_code_obj(code_obj, scope)?;
            // vm.run_code_obj(code_obj, scope);

            // // Ok(())
        // });
    
    };

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
