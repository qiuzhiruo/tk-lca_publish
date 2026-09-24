//Maya ASCII 2015 scene
//Name: template.ma
//Last modified: Wed, May 27, 2015 11:41:43 AM
//Codeset: 936
requires maya "2015";
requires -nodeType "assemblyDefinition" "sceneAssembly" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201410051530-933320";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode assemblyDefinition -n "{ASSET}";
	setAttr ".isc" yes;
	setAttr ".icn" -type "string" "out_assemblyDefinition.png";
	setAttr ".ctor" -type "string" "liulu";
	setAttr ".cdat" -type "string" "2015/05/27 10:11:58";
	setAttr -s 2 ".rep";
	setAttr ".rep[0].rna" -type "string" "{ASSET}.abc";
	setAttr ".rep[0].rla" -type "string" "{ASSET}.abc";
	setAttr ".rep[0].rty" -type "string" "Cache";
	setAttr ".rep[0].rda" -type "string" "{GPU_CACHE_PROXY}";
    setAttr ".rep[1].rna" -type "string" "{ASSET}.locator";
	setAttr ".rep[1].rla" -type "string" "{ASSET}.locator";
	setAttr ".rep[1].rty" -type "string" "Locator";
	setAttr ".rep[1].rda" -type "string" "{ASSET}";
	setAttr ".rep[2].rna" -type "string" "{ASSET}.proxy.abc";
	setAttr ".rep[2].rla" -type "string" "{ASSET}.proxy.abc";
	setAttr ".rep[2].rty" -type "string" "Cache";
	setAttr ".rep[2].rda" -type "string" "{GPU_CACHE_PROXY}";
	setAttr ".rep[3].rna" -type "string" "{ASSET}.ma";
	setAttr ".rep[3].rla" -type "string" "{ASSET}.ma";
	setAttr ".rep[3].rty" -type "string" "Scene";
	setAttr ".rep[3].rda" -type "string" "{MAYA_FILE}";
// End of template.ma
