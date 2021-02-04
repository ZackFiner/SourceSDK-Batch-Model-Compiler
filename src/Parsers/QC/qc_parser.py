import plyplus
from plyplus import Grammar

def naive_parse(filepath):
    fp = open(filepath, 'r')
    f_data = fp.readlines()


grammar = r"""
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
"""

qc_parser = Grammar(grammar)
qc_example = """
// line comment with stuff
$ModelName "props\cs_office\Chair_office.mdl"

$StaticProp

$BodyGroup "Body"
{
	studio "chair_office_reference.smd"
}


$SurfaceProp "plastic_box"

$Contents "solid"

$CDMaterials "models\props\cs_office\"

$CBox 0 0 0 0 0 0

$BBox -13.561 -12.791 -0.281 13.299 12.791 47.777


$Sequence "idle" {
	"chair_office_anims\idle.smd"
	activity "act_idle" 1
	fadein 0.2
	fadeout 0.2
	fps 30
}

$CollisionModel "chair_office_physics.smd"
{
	$mass 15
	$inertia 1
	$damping 0
	$rotdamping 0
	$rootbone " "
	$concave

}

$KeyValues
{
	prop_data 
	{
		"base" "Cloth.Large"
	}
}

"""

result = qc_parser.parse(qc_example)

print(result.pretty())

