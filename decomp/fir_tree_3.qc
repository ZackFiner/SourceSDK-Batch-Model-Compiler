// Created by Crowbar 0.42.0.0

$ModelName "ost/fir_tree_3.mdl"

$StaticProp

$BodyGroup "body"
{
	studio "fir_tree_3_reference.smd"
}


$SurfaceProp "wood"

$Contents "solid"

$MaxEyeDeflection 90

$CDMaterials "models\ost\foliage\"
$CDMaterials ""

$CBox 0 0 0 0 0 0

$BBox -217.128 -232.384 -5.98 219.794 185.948 913.368


$Sequence "ref" {
	"fir_tree_3_anims\ref.smd"
	fadein 0.2
	fadeout 0.2
	fps 30
}

$CollisionModel "fir_tree_3_physics.smd"
{
	$mass 7273.577
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
		"value" "models\props\hr_massive\ported_foliage\fir_tree_3.qc"
	}
}
