start: qc;

qc: (qc_cmd)+;
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
LINECOMMENT: '(//|#|;).*\n' (%ignore); // ignore line comments like this one
BLOCKCOMMENT: '/[*](.|\n)*[*]/' (%ignore); // ignore /* block comments */
WHITESPACE: '[ \n\t]+' (%ignore);