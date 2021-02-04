start: qc;

// rules
?qc: qc_cmd*;
?qc_cmd: command ?params ?body
?body: '\{' (qc_cmd | params | )*

//tokens
label:
string: '"[^"]*"' ;
number: '-?([1-9]\d*|\d)(\.\d+)?([eE][+-]?\d+)' ;
command: '\$'(command_name);

