//@+leo-ver=5-thin
//@+node:ekr.20231120070819.1: * @file ../rust/orange/src/main.rs
//@@language rust
// Orange in rust.

//@+others
//@+node:ekr.20231226041126.1: ** fn main
fn main() {
    println!("main.rs: ekr-orange");
}
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
