//Maya ASCII 2015 scene
//Name: global_control.ma
//Last modified: Wed, Feb 22, 2017 03:38:15 PM
//Codeset: 936
requires maya "2015";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201503261530-955654";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "rig";
createNode transform -n "anim_rig" -p "rig";
lockNode -l 1 ;
createNode transform -n "anim_controls_grp" -p "anim_rig";
lockNode -l 1 ;
createNode transform -n "global_ctrl_zero" -p "anim_controls_grp";
createNode transform -n "global_ctrl_PH" -p "global_ctrl_zero";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -k on ".pivot_vis";
createNode transform -n "global_ctrl_SN" -p "global_ctrl_PH";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -k on ".pivot_vis";
createNode transform -n "global_ctrl" -p "global_ctrl_SN";
	addAttr -ci true -sn "gs" -ln "globalScale" -dv 1 -at "double";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -k on ".gs";
	setAttr -k on ".pivot_vis";
createNode nurbsCurve -n "global_ctrlShape" -p "global_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.39197588843170594 2.3938533429996536e-017 -0.39197588843170533
		-6.3243293924914355e-017 3.3880322023027517e-017 -0.55433761754336275
		-0.3919758884317055 2.3938533429996558e-017 -0.3919758884317055
		-0.55433761754336275 -6.3067425544889497e-020 -1.6063317313186768e-016
		-0.3919758884317055 -2.4064668281086389e-017 0.39197588843170533
		-1.6703274268436293e-016 -3.4006456874117296e-017 0.55433761754336275
		0.39197588843170533 -2.4064668281086389e-017 0.3919758884317055
		0.55433761754336275 -6.306742554491764e-020 2.9773581574803636e-016
		0.39197588843170594 2.3938533429996536e-017 -0.39197588843170533
		-6.3243293924914355e-017 3.3880322023027517e-017 -0.55433761754336275
		-0.3919758884317055 2.3938533429996558e-017 -0.3919758884317055
		;
createNode transform -n "root_ctrl_zero" -p "global_ctrl";
createNode transform -n "root_ctrl_PH" -p "root_ctrl_zero";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "root_ctrl_SN" -p "root_ctrl_PH";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "root_ctrl" -p "root_ctrl_SN";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -k on ".pivot_vis";
createNode nurbsCurve -n "root_ctrlShape" -p "root_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 86 0 no 3
		91 15.745750770000001 15.745750770000001 15.745750770000001 15.994336930000005
		 15.994336930000005 15.994336930000005 16.994336930000003 16.994336930000003 16.994336930000003
		 17.994336930000003 17.994336930000003 17.994336930000003 18.994336930000003 18.994336930000003
		 18.994336930000003 19.994336930000003 19.994336930000003 19.994336930000003 20.253014204999999
		 20.253014204999999 20.253014204999999 20.885202119999999 21.502214874 21.502214874
		 21.502214874 21.758286319 21.758286319 21.758286319 22.758286319 22.758286319 22.758286319
		 23.758286319 23.758286319 23.758286319 24.758286319 24.758286319 24.758286319 25.758286319
		 25.758286319 25.758286319 26.014851714999999 26.014851714999999 26.014851714999999
		 26.633484611 27.244006168999999 27.244006168999999 27.244006168999999 27.495894292999999
		 27.495894292999999 27.495894292999999 28.495894292999999 28.495894292999999 28.495894292999999
		 29.495894292999999 29.495894292999999 29.495894292999999 30.495894292999999 30.495894292999999
		 30.495894292999999 31.495894292999999 31.495894292999999 31.495894292999999 31.758026582999999
		 31.758026582999999 31.758026582999999 32.371381249000002 32.991210664 32.991210664
		 32.991210664 33.247937673999999 33.247937673999999 33.247937673999999 34.247937673999999
		 34.247937673999999 34.247937673999999 35.247937673999999 35.247937673999999 35.247937673999999
		 36.247937673999999 36.247937673999999 36.247937673999999 37.247937673999999 37.247937673999999
		 37.247937673999999 37.502186903999998 37.502186903999998 37.502186903999998 38.121090553499997
		 38.742038981499995 38.742038981499995 38.742038981499995
		89
		0.078423928214034211 -6.6272686110353284e-020 0.25521040335560868
		0.078423928214034211 -1.8025331156606683e-017 0.27470550652245107
		0.078423928214034211 1.7892785784385926e-017 0.29420060968929318
		0.078423928214034211 -6.6272686110353284e-020 0.3136957128561369
		0.10456523761871173 1.7892785784385926e-017 0.3136957128561374
		0.13070654702338994 1.7892785784385926e-017 0.3136957128561374
		0.15684785642806842 -9.0458019213585047e-018 0.31369571285613623
		0.10456523761871173 -3.5984389627102972e-017 0.36597833166549282
		0.052282618809355863 -5.3943448097599418e-017 0.4182609504748469
		7.1902498153548981e-033 1.7892785784385926e-017 0.4705435692842031
		-0.052282618809355863 -5.3943448097599418e-017 0.4182609504748469
		-0.10456523761871173 -7.1902506568095785e-017 0.36597833166549282
		-0.15684785642806842 -6.6272686110353284e-020 0.3136957128561369
		-0.13070654702338994 -6.6272686110353284e-020 0.3136957128561369
		-0.10456523761871173 -4.4963918862351183e-017 0.31369571285613579
		-0.078423928214034211 -6.6272686110353284e-020 0.3136957128561369
		-0.078423928214034211 8.9132565491377936e-018 0.29340922481093301
		-0.078423928214034211 3.5851844254882252e-017 0.27312273676573184
		-0.075739518410486054 2.6872315019634038e-017 0.25502568379334067
		-0.1179710735972416 5.3810902725378439e-017 0.24234830725438475
		-0.19550260682322096 -6.6272686110353284e-020 0.19699539441113387
		-0.24124173058056783 -9.0458019213585047e-018 0.11985007209925148
		-0.25344932699510414 -6.6272686110353284e-020 0.078423928214034225
		-0.27353145561544778 -2.3111549949223921e-018 0.078423928214034155
		-0.29361358423579198 4.4234919315137429e-018 0.078423928214034155
		-0.31369571285613684 -6.6272686110353284e-020 0.078423928214034225
		-0.3136957128561369 -1.3535566538982609e-017 0.10456523761871173
		-0.3136957128561369 -4.5560373037344217e-018 0.13070654702338999
		-0.31369571285613684 8.9132565491377936e-018 0.1568478564280687
		-0.36597833166549282 -3.1494625009478959e-017 0.10456523761871173
		-0.4182609504748469 -9.0458019213585047e-018 0.052282618809355863
		-0.4705435692842031 -9.6739698366203143e-020 4.110603767479524e-020
		-0.4182609504748469 1.1158138857949835e-017 -0.052282618809355863
		-0.36597833166549282 1.3403021166761868e-017 -0.10456523761871173
		-0.3136957128561369 4.4234919315137429e-018 -0.15684785642806812
		-0.31369571285613684 4.4234919315137429e-018 -0.13070654702338994
		-0.31369571285613684 1.3403021166761868e-017 -0.10456523761871173
		-0.31369571285613684 -6.6272686110353284e-020 -0.078423928214034225
		-0.29357484665802558 -6.6272686110353284e-020 -0.078423928214034225
		-0.27345398045991726 -4.5560373037344217e-018 -0.078423928214034377
		-0.25419607047809967 -5.8433212715223561e-017 -0.078451853152432291
		-0.24136031917192999 -4.4963918862351183e-017 -0.11964991245878144
		-0.19639575308671456 -6.2922977332847487e-017 -0.19559783702587172
		-0.12065095099714372 -4.4963918862351183e-017 -0.24076552558860792
		-0.078423928214033684 -2.7004860391854786e-017 -0.25443354439250465
		-0.078423928214033684 -6.6272686110353284e-020 -0.27418760054704805
		-0.078423928214033684 8.9132565491377936e-018 -0.2939416567015915
		-0.078423928214033628 -6.6272686110353284e-020 -0.3136957128561369
		-0.10456523761871156 -1.8025331156606683e-017 -0.3136957128561374
		-0.13070654702338991 -1.8025331156606683e-017 -0.3136957128561374
		-0.15684785642806756 -1.8025331156606683e-017 -0.3136957128561374
		-0.10456523761871156 7.1769961195874848e-017 -0.36597833166549282
		-0.052282618809355717 5.3810902725378439e-017 -0.4182609504748469
		-7.1902498153548981e-033 -1.8025331156606683e-017 -0.4705435692842031
		0.052282618809355863 5.3810902725378439e-017 -0.4182609504748469
		0.10456523761871173 7.1769961195874848e-017 -0.36597833166549282
		0.15684785642806842 -6.6272686110353284e-020 -0.3136957128561369
		0.13070654702338994 -6.6272686110353284e-020 -0.3136957128561369
		0.10456523761871173 2.6872315019634038e-017 -0.31369571285613512
		0.078423928214034211 -6.6272686110353284e-020 -0.3136957128561369
		0.078423928214034211 2.6872315019634038e-017 -0.29313826896259582
		0.078423928214034211 -1.8025331156606683e-017 -0.27258082506905529
		0.079505717115411642 -5.3943448097599418e-017 -0.25386538535642467
		0.12030161539808663 -1.8025331156606683e-017 -0.24097357827131177
		0.19636591591812411 8.9132565491377936e-018 -0.1957289918721746
		0.24144783141554149 1.3403021166761868e-017 -0.11950202045041716
		0.25329509104760439 -6.6272686110353284e-020 -0.078423928214034225
		0.27342863165044873 2.178609622701689e-018 -0.078423928214034155
		0.29356217225329101 -4.5560373037344217e-018 -0.078423928214034155
		0.31369571285613684 -6.6272686110353284e-020 -0.078423928214034225
		0.3136957128561369 1.3403021166761868e-017 -0.10456523761871173
		0.3136957128561369 4.4234919315137429e-018 -0.13070654702338999
		0.31369571285613684 -9.0458019213585047e-018 -0.1568478564280687
		0.36597833166549282 3.1362079637258146e-017 -0.10456523761871173
		0.4182609504748469 8.9132565491377936e-018 -0.052282618809355863
		0.4705435692842031 -9.6739698366203034e-020 4.1106037674801108e-020
		0.4182609504748469 -6.6272686110353284e-020 0.05228261880935578
		0.36597833166549282 -1.3535566538982609e-017 0.10456523761871173
		0.3136957128561369 -4.5560373037344217e-018 0.15684785642806812
		0.31369571285613684 -4.5560373037344217e-018 0.13070654702338994
		0.31369571285613684 -1.3535566538982609e-017 0.10456523761871173
		0.31369571285613684 -6.6272686110353284e-020 0.078423928214034225
		0.29375648949414224 -6.6272686110353284e-020 0.078423928214034225
		0.27381726613214968 4.4234919315137429e-018 0.078423928214034377
		0.25387804277015524 -6.6272686110353284e-020 0.078423928214034225
		0.24138012692795052 5.8300667343002526e-017 0.11961645192141336
		0.1960310626951528 6.2790431960626662e-017 0.19623220849946024
		0.11936365554086116 7.1769961195874848e-017 0.24152962215601281
		0.077989117605465771 7.1769961195874848e-017 0.2543397906674264
		;
createNode transform -n "root_piv_ctrl" -p "root_ctrl";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_piv_ctrlShape" -p "root_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "root_piv_ctrlShape1" -p "root_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "root_piv_ctrlShape2" -p "root_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "root_base" -p "root_ctrl";
createNode transform -n "root_ctrl_SN_piv_ctrl" -p "root_ctrl_SN";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape" -p "root_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape1" -p "root_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape2" -p "root_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "root_ctrl_PH_piv_ctrl" -p "root_ctrl_PH";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape" -p "root_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape1" -p "root_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape2" -p "root_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "global_piv_ctrl" -p "global_ctrl";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_piv_ctrlShape" -p "global_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "global_piv_ctrlShape1" -p "global_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "global_piv_ctrlShape2" -p "global_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "global_ctrl_SN_piv_ctrl" -p "global_ctrl_SN";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape" -p "global_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape1" -p "global_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape2" -p "global_ctrl_SN_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "global_ctrl_PH_piv_ctrl" -p "global_ctrl_PH";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape" -p "global_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20000000000000001 0 0
		;
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape1" -p "global_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20000000000000001 0
		;
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape2" -p "global_ctrl_PH_piv_ctrl";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20000000000000001
		;
createNode transform -n "anim_skeletons_grp" -p "anim_rig";
lockNode -l 1 ;
createNode transform -n "anim_modules_grp" -p "anim_rig";
lockNode -l 1 ;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "global_ctrl_PH_piv_ctrl.tx" "global_ctrl_PH.rpx";
connectAttr "global_ctrl_PH_piv_ctrl.ty" "global_ctrl_PH.rpy";
connectAttr "global_ctrl_PH_piv_ctrl.tz" "global_ctrl_PH.rpz";
connectAttr "global_ctrl_PH_piv_ctrl.tx" "global_ctrl_PH.spx";
connectAttr "global_ctrl_PH_piv_ctrl.ty" "global_ctrl_PH.spy";
connectAttr "global_ctrl_PH_piv_ctrl.tz" "global_ctrl_PH.spz";
connectAttr "global_ctrl_SN_piv_ctrl.tx" "global_ctrl_SN.rpx";
connectAttr "global_ctrl_SN_piv_ctrl.ty" "global_ctrl_SN.rpy";
connectAttr "global_ctrl_SN_piv_ctrl.tz" "global_ctrl_SN.rpz";
connectAttr "global_ctrl_SN_piv_ctrl.tx" "global_ctrl_SN.spx";
connectAttr "global_ctrl_SN_piv_ctrl.ty" "global_ctrl_SN.spy";
connectAttr "global_ctrl_SN_piv_ctrl.tz" "global_ctrl_SN.spz";
connectAttr "global_piv_ctrl.tx" "global_ctrl.rpx";
connectAttr "global_piv_ctrl.ty" "global_ctrl.rpy";
connectAttr "global_piv_ctrl.tz" "global_ctrl.rpz";
connectAttr "global_piv_ctrl.tx" "global_ctrl.spx";
connectAttr "global_piv_ctrl.ty" "global_ctrl.spy";
connectAttr "global_piv_ctrl.tz" "global_ctrl.spz";
connectAttr "root_ctrl_PH_piv_ctrl.tx" "root_ctrl_PH.rpx";
connectAttr "root_ctrl_PH_piv_ctrl.ty" "root_ctrl_PH.rpy";
connectAttr "root_ctrl_PH_piv_ctrl.tz" "root_ctrl_PH.rpz";
connectAttr "root_ctrl_PH_piv_ctrl.tx" "root_ctrl_PH.spx";
connectAttr "root_ctrl_PH_piv_ctrl.ty" "root_ctrl_PH.spy";
connectAttr "root_ctrl_PH_piv_ctrl.tz" "root_ctrl_PH.spz";
connectAttr "root_ctrl_SN_piv_ctrl.tx" "root_ctrl_SN.rpx";
connectAttr "root_ctrl_SN_piv_ctrl.ty" "root_ctrl_SN.rpy";
connectAttr "root_ctrl_SN_piv_ctrl.tz" "root_ctrl_SN.rpz";
connectAttr "root_ctrl_SN_piv_ctrl.tx" "root_ctrl_SN.spx";
connectAttr "root_ctrl_SN_piv_ctrl.ty" "root_ctrl_SN.spy";
connectAttr "root_ctrl_SN_piv_ctrl.tz" "root_ctrl_SN.spz";
connectAttr "root_piv_ctrl.tx" "root_ctrl.rpx";
connectAttr "root_piv_ctrl.ty" "root_ctrl.rpy";
connectAttr "root_piv_ctrl.tz" "root_ctrl.rpz";
connectAttr "root_piv_ctrl.tx" "root_ctrl.spx";
connectAttr "root_piv_ctrl.ty" "root_ctrl.spy";
connectAttr "root_piv_ctrl.tz" "root_ctrl.spz";
connectAttr "root_ctrl.pivot_vis" "root_piv_ctrl.v" -l on;
connectAttr "root_ctrl_SN.pivot_vis" "root_ctrl_SN_piv_ctrl.v" -l on;
connectAttr "root_ctrl_PH.pivot_vis" "root_ctrl_PH_piv_ctrl.v" -l on;
connectAttr "global_ctrl.pivot_vis" "global_piv_ctrl.v" -l on;
connectAttr "global_ctrl_SN.pivot_vis" "global_ctrl_SN_piv_ctrl.v" -l on;
connectAttr "global_ctrl_PH.pivot_vis" "global_ctrl_PH_piv_ctrl.v" -l on;
// End of global_control.ma
