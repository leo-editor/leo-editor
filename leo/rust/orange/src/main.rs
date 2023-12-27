

// pub fn main() -> std::process::ExitCode {
    // // Run the orange binary.
    // println!("orange/src/main.rs");

    // orange::run()
// }

// hello_embed.rs:
use rustpython_vm as vm;

fn main() -> vm::PyResult<()> {
    vm::Interpreter::without_stdlib(Default::default()).enter(|vm| {
        let scope = vm.new_scope_with_builtins();
        let source = r#"print("Hello World!")"#;
        let code_obj = vm
            .compile(source, vm::compiler::Mode::Exec, "<embedded>".to_owned())
            .map_err(|err| vm.new_syntax_error(&err, Some(source)))?;

        vm.run_code_obj(code_obj, scope)?;

        Ok(())
    })
}
