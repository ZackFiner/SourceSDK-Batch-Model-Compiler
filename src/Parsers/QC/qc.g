start: qc;

// rules
qc: qc_cmd+;
qc_cmd: '\$'command_name params;
?params: (literal|body|label)*;
command_name: '\w+';

body: '\{'(qc_cmd|literal|body|label)'\}';
@literal: (number|string);
label: '\w+';

string: '".*"';
number: '-?([1-9]\d*|\d)(\.\d+)?([eE][+-]?\d+)';
commnad_start_symbol: '\$';
WHITESPACE: '[ \n\t]+' (%ignore);