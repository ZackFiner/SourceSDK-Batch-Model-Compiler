// Created by Crowbar 0.42.0.0

$ModelName "ost/fir_tree_1.mdl"

$StaticProp

$BodyGroup "body"
{
	studio "fir_tree_1_reference.smd"
}


$SurfaceProp "wood"

$Contents "solid"

$MaxEyeDeflection 90

$CDMaterials "models\ost\foliage\"
$CDMaterials ""

$CBox 0 0 0 0 0 0

$BBox -128.759 -158.096 -4.16 152.9 129.355 635.386


$Sequence "ref" {
	"fir_tree_1_anims\ref.smd"
	fadein 0.2
	fadeout 0.2
	fps 30
}

$CollisionModel "fir_tree_1_physics.smd"
{
	$mass 2410.708
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
		"value" "models\props\hr_massive\ported_foliage\fir_tree_1.qc"
	}
}
