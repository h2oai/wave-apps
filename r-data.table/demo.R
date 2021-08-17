library(h2owave)
serve <- function(qo)
{
  qo$client$test <- ifelse(is.null(qo$client$test), 0, qo$client$test)
  ifelse(qo$args$choose_file==TRUE,qo$client$test <- qo$client$test + 1, qo$client$test <- 0)
  print(qo$args)
  print(qo$page)
  if (length(qo$args)==0) {
    qo$page$add_card("example",ui_form_card(
      box='1 1 12 10'
      ,items = list(
        ui_button(name='choose_file', label="Choose file ...", primary=TRUE)
      )
    ))
  } else if (isTRUE(qo$args$choose_file)) {
    qo$page$add_card('meta', ui_meta_card(box='',
      scripts=list(
        ui_script('https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css'),
        ui_script('https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js')
      ),
      script=ui_inline_script(
        content="$(document).ready( function () {
                   $('#myTable').DataTable();
                 } );",
        requires='dataTables',
        targets='myTable'
      )
    ))
    qo$page$add_card('table', ui_markup_card(
      box='1 1 -1 -1',
      title='First DataTables table',
      content="<table id='myTable'>
				<thead>
					<tr>
						<th>Name</th>
						<th>Position</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>Tiger Nixon</td>
						<td>System Architect</td>
					</tr>
					<tr>
						<td>Garrett Winters</td>
						<td>Accountant</td>
					</tr>
				</tbody>
				<tfoot>
					<tr>
						<th>Name</th>
						<th>Position</th>
					</tr>
				</tfoot>
			</table>"
    ))
  } else if (isTRUE(qo$args$action1)) {
    print(args(qo$page$set))
    qo$page$set("table","items","2","textbox","value","'oranges'")  # double quote last value!
  }
  cat("finished serve()\n=====================\n\n")
  qo$page$save()
}
app("/demo")

