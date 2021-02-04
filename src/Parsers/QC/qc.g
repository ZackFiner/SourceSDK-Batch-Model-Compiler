start: qc;

qc: (qc_cmd|line_comment)+;
qc_cmd: '\$'command_name param*;
param: (literal|body|label);
command_name: '\w+';

body: '\{'(qc_cmd|literal|body|label)*'\}';
@literal: (number|string);
label: label_name label_param*;
label_name: '\w+';
label_param: (literal|body);

string: '".*"';
number: '-?(\d+)(.\d+)?(e-?\d+)?';
commnad_start_symbol: '\$';
line_comment: '//(\w+|\s+)*';
WHITESPACE: '[ \n\t]+' (%ignore);