fn main() {
    let mut df = hydroflow::hydroflow_syntax! {
        a = source_iter(0..10);
        loop {
            loop {
                a -> batch() -> null();
            }
        }
    };
    df.run_available();
}