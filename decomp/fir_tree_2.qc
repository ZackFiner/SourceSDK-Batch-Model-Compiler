// Created by Crowbar 0.42.0.0

$ModelName "ost/fir_tree_2.mdl"

$StaticProp

$BodyGroup "body"
{
	studio "fir_tree_2_reference.smd"
}


$SurfaceProp "wood"

$Contents "solid"

$MaxEyeDeflection 90

$CDMaterials "models\ost\foliage\"
$CDMaterials ""

$CBox 0 0 0 0 0 0

$BBox -188.807 -197.619 -5.2 191.125 161.694 794.233


$Sequence "ref" {
	"fir_tree_2_anims\ref.smd"
	fadein 0.2
	fadeout 0.2
	fps 30
}

$CollisionModel "fir_tree_2_physics.smd"
{
	$mass 4880.089
	$inertia 1
	$damping 0
	$rotdamping 1
	$rootbone " "
	$concave

}

$KeyValues
{
	qc_path 
	{
		"value" "models\props\hr_massive\ported_foliage\fir_tree_2.qc"
	}
}
