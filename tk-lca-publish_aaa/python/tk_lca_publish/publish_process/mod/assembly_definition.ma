//Maya ASCII 2019 scene
//Name: template_2019.ma
//Last modified: Fri, May 24, 2024 02:15:50 PM
//Codeset: UTF-8
requires maya "2019";
requires -nodeType "assemblyDefinition" "sceneAssembly" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2019";
fileInfo "version" "2019";
fileInfo "cutIdentifier" "202003131251-bd5bbc395a";
fileInfo "osv" "Linux 3.10.0-1160.102.1.el7.x86_64 #1 SMP Tue Oct 17 15:42:21 UTC 2023 x86_64";
createNode assemblyDefinition -n "{ASSET}";
	setAttr ".isc" yes;
	setAttr ".icn" -type "string" "out_assemblyDefinition.png";
	setAttr ".ctor" -type "string" "xiaoyu2";
	setAttr ".cdat" -type "string" "2024/05/24 14:14:48";
	setAttr -s 6 ".rep";
	setAttr ".rep[0].rna" -type "string" "{ASSET}.abc";
	setAttr ".rep[0].rla" -type "string" "{ASSET}.abc";
	setAttr ".rep[0].rty" -type "string" "Cache";
	setAttr ".rep[0].rda" -type "string" "{GPU_CACHE_PROXY}";
	setAttr ".rep[1].rna" -type "string" "{ASSET}.hi.abc";
	setAttr ".rep[1].rla" -type "string" "{ASSET}.hi.abc";
	setAttr ".rep[1].rty" -type "string" "Cache";
	setAttr ".rep[1].rda" -type "string" "{GPU_CACHE_HI}";
    setAttr ".rep[2].rna" -type "string" "{ASSET}.proxy.abc";
	setAttr ".rep[2].rla" -type "string" "{ASSET}.proxy.abc";
	setAttr ".rep[2].rty" -type "string" "Cache";
	setAttr ".rep[2].rda" -type "string" "{GPU_CACHE_PROXY}";
    setAttr ".rep[3].rna" -type "string" "{ASSET}.color_id.abc";
	setAttr ".rep[3].rla" -type "string" "{ASSET}.color_id.abc";
	setAttr ".rep[3].rty" -type "string" "Cache";
	setAttr ".rep[3].rda" -type "string" "{GPU_CACHE_COLOR_ID}";
	setAttr ".rep[4].rna" -type "string" "{ASSET}.ma";
	setAttr ".rep[4].rla" -type "string" "{ASSET}.ma";
	setAttr ".rep[4].rty" -type "string" "Scene";
	setAttr ".rep[4].rda" -type "string" "{MAYA_FILE}";
	setAttr ".rep[5].rna" -type "string" "{ASSET}.hi.mb";
	setAttr ".rep[5].rla" -type "string" "{ASSET}.hi.mb";
	setAttr ".rep[5].rty" -type "string" "Scene";
	setAttr ".rep[5].rda" -type "string" "{MAYA_FILE_hi}";
    setAttr ".rep[6].rna" -type "string" "{ASSET}_lay_rig.ma";
	setAttr ".rep[6].rla" -type "string" "{ASSET}_lay_rig.ma";
	setAttr ".rep[6].rty" -type "string" "Scene";
	setAttr ".rep[6].rda" -type "string" "{MAYA_FILE_Lay_rig}";
	setAttr ".rep[7].rna" -type "string" "{ASSET}.locator";
	setAttr ".rep[7].rla" -type "string" "{ASSET}.locator";
	setAttr ".rep[7].rty" -type "string" "Locator";
	setAttr ".rep[7].rda" -type "string" "{ASSET}";

// End of template_2019.ma
