use super::{OperatorConstraints, WriteContextArgs, WriteIteratorArgs, RANGE_0, RANGE_1};

use quote::quote_spanned;
use syn::parse_quote;

/// > 2 input streams of type S and T, 1 output stream of type (S, T)
///
/// Forms the cross-join (Cartesian product) of the items in the input streams, returning all
/// tupled pairs.
///
/// ```hydroflow
/// // should print all 4 pairs of emotion and animal
/// my_join = cross_join();
/// source_iter(vec!["happy", "sad"]) -> [0]my_join;
/// source_iter(vec!["dog", "cat"]) -> [1]my_join;
/// my_join -> for_each(|(v1, v2)| println!("({}, {})", v1, v2));
/// ```
///
/// `cross_join` can also be provided with one or two generic lifetime persistence arguments
/// in the same was as [`join`](#join), see [`join`'s documentation](#join) for more info.
///
/// ```rustbook
/// let (input_send, input_recv) = hydroflow::util::unbounded_channel::<&str>();
/// let mut flow = hydroflow::hydroflow_syntax! {
///     my_join = cross_join::<'tick>();
///     source_iter(["hello", "bye"]) -> [0]my_join;
///     source_stream(input_recv) -> [1]my_join;
///     my_join -> for_each(|(s, t)| println!("({}, {})", s, t));
/// };
/// input_send.send("oakland").unwrap();
/// flow.run_tick();
/// input_send.send("san francisco").unwrap();
/// flow.run_tick();
/// ```
/// Prints only `"(hello, oakland)"` and `"(bye, oakland)"`. The `source_iter` is only included in
/// the first tick, then forgotten.
#[hydroflow_internalmacro::operator_docgen]
pub const CROSS_JOIN: OperatorConstraints = OperatorConstraints {
    name: "cross_join",
    hard_range_inn: &(2..=2),
    soft_range_inn: &(2..=2),
    hard_range_out: RANGE_1,
    soft_range_out: RANGE_1,
    num_args: 0,
    persistence_args: &(0..=2),
    type_args: RANGE_0,
    is_external_input: false,
    ports_inn: Some(&(|| super::PortListSpec::Fixed(parse_quote! { 0, 1 }))),
    ports_out: None,
    input_delaytype_fn: &|_| None,
    write_fn: &(|wc @ &WriteContextArgs { op_span, .. },
                 wi @ &WriteIteratorArgs { ident, inputs, .. },
                 diagnostics| {
        let mut output = (super::join::JOIN.write_fn)(wc, wi, diagnostics)?;

        let lhs = &inputs[0];
        let rhs = &inputs[1];
        let write_iterator = output.write_iterator;
        output.write_iterator = quote_spanned!(op_span=>
            let #lhs = #lhs.map(|a| ((), a));
            let #rhs = #rhs.map(|b| ((), b));
            #write_iterator
            let #ident = #ident.map(|((), (a, b))| (a, b));
        );

        Ok(output)
    }),
};
