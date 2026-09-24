//Maya ASCII 2019 scene
//Name: global_control_prp.ma
//Last modified: Wed, Apr 29, 2026 05:01:10 PM
//Codeset: UTF-8
requires maya "2019";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2019";
fileInfo "version" "2019";
fileInfo "cutIdentifier" "202003131251-bd5bbc395a";
fileInfo "osv" "Linux 3.10.0-957.el7.x86_64 #1 SMP Thu Nov 8 23:39:32 UTC 2018 x86_64";
createNode transform -n "rig";
	rename -uid "A6F5B9A7-4EAE-5112-8C04-E2B99B617D0A";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
createNode transform -n "anim_rig" -p "rig";
	rename -uid "17ECF4DD-4EED-03B4-A9CF-5BADCD25D53E";
lockNode -l 1 ;
createNode transform -n "anim_controls_grp" -p "anim_rig";
	rename -uid "5796AD9F-44E7-F8A0-A33B-9492AA20D0A1";
lockNode -l 1 ;
createNode transform -n "global_ctrl_zero" -p "anim_controls_grp";
	rename -uid "9DAF4799-4260-52B2-2E58-7183D8C75B8F";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "global_ctrl_PH" -p "global_ctrl_zero";
	rename -uid "D0292C82-4496-3B11-C35F-29B9FA77242E";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "global_ctrl_SN" -p "global_ctrl_PH";
	rename -uid "4F2FC581-400F-31BF-3525-358BE1C861CB";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "global_ctrl" -p "global_ctrl_SN";
	rename -uid "7FAA8599-4775-1EB7-9D0C-3DB21A90B93E";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	addAttr -ci true -sn "global_scale" -ln "global_scale" -dv 1 -at "double";
	setAttr -l on -k off ".v";
	setAttr -k on ".pivot_vis";
createNode nurbsCurve -n "global_ctrlShape" -p "global_ctrl";
	rename -uid "401B842A-4EA4-88FC-249C-A5998C8C2FBD";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0.39217266344591917 2.3950550764212628e-17 -0.39217266344591861
		-6.327504256157351e-17 3.3897330214205564e-17 -0.55461589943719936
		-0.39217266344591878 2.3950550764212647e-17 -0.39217266344591878
		-0.55461589943719936 -6.3099085894222827e-20 -1.6071381226263822e-16
		-0.39217266344591878 -2.4076748936001144e-17 0.39217266344591861
		-1.6711659444995827e-16 -3.402352838599401e-17 0.55461589943719936
		0.39217266344591861 -2.4076748936001144e-17 0.39217266344591878
		0.55461589943719936 -6.3099085894250981e-20 2.9788528149607008e-16
		0.39217266344591917 2.3950550764212628e-17 -0.39217266344591861
		-6.327504256157351e-17 3.3897330214205564e-17 -0.55461589943719936
		-0.39217266344591878 2.3950550764212647e-17 -0.39217266344591878
		;
createNode transform -n "gr_middle_a_ctrl_SN" -p "global_ctrl";
	rename -uid "C71EF74C-4717-1E67-5B6D-B691A3BD2EA4";
createNode transform -n "gr_middle_a_sec_ctrl" -p "gr_middle_a_ctrl_SN";
	rename -uid "662679C0-0001-D20A-69F1-C8AD00000351";
createNode transform -n "gr_middle_a_pri_ctrl" -p "gr_middle_a_sec_ctrl";
	rename -uid "662679C0-0001-D20A-69F1-C8A500000350";
createNode transform -n "gr_middle_a_ctrl" -p "gr_middle_a_pri_ctrl";
	rename -uid "1AB4BB3C-432E-2D9C-9B8F-DCB40B3E9E64";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "gr_middle_a_ctrlShape" -p "gr_middle_a_ctrl";
	rename -uid "04BF380C-40EC-CFD7-E9DF-0C967785F342";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0.33743422600483991 2.0661887239979565e-17 -0.3374342260048398
		3.5991506579932265e-18 2.9220321159002708e-17 -0.47720405882491257
		-0.3374342260048398 2.0661887239979568e-17 -0.33743422600483985
		-0.4772040588249129 1.1008508313054737e-32 -1.5901123605244388e-16
		-0.33743422600483985 -2.0661887239979565e-17 0.3374342260048398
		-7.7197574888181871e-17 -2.9220321159002714e-17 0.47720405882491307
		0.33743422600483974 -2.0661887239979571e-17 0.33743422600483985
		0.4772040588249129 -2.0611855611269931e-34 2.4137519604705661e-17
		0.33743422600483991 2.0661887239979565e-17 -0.3374342260048398
		3.5991506579932265e-18 2.9220321159002708e-17 -0.47720405882491257
		-0.3374342260048398 2.0661887239979568e-17 -0.33743422600483985
		;
createNode transform -n "gr_middle_b_ctrl_SN" -p "gr_middle_a_ctrl";
	rename -uid "02017540-4DF8-C4DF-289F-BEB0B604348B";
createNode transform -n "gr_middle_b_sec_ctrl" -p "gr_middle_b_ctrl_SN";
	rename -uid "662679C0-0001-D20A-69F1-C88C0000034F";
createNode transform -n "gr_middle_b_pri_ctrl" -p "gr_middle_b_sec_ctrl";
	rename -uid "662679C0-0001-D20A-69F1-C8700000034E";
createNode transform -n "gr_middle_b_ctrl" -p "gr_middle_b_pri_ctrl";
	rename -uid "FF973DE4-4B22-73AE-82E2-6DA755E05CC6";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "gr_middle_b_ctrlShape" -p "gr_middle_b_ctrl";
	rename -uid "65E16018-4BEB-BB36-D53C-DC9BD28FE516";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0.28611163533215767 1.7519284920417063e-17 -0.28611163533215772
		2.4776010337532285e-17 2.4776010337532285e-17 -0.40462295503948226
		-0.28611163533215767 1.7519284920417063e-17 -0.28611163533215767
		-0.40462295503948265 6.5399460244645835e-33 -5.5491717416657685e-17
		-0.28611163533215767 -1.751928492041706e-17 0.28611163533215767
		-4.0531358140615173e-17 -2.4776010337532297e-17 0.40462295503948287
		0.28611163533215767 -1.7519284920417063e-17 0.28611163533215767
		0.40462295503948265 1.8768574915819683e-33 2.0662297538988987e-17
		0.28611163533215767 1.7519284920417063e-17 -0.28611163533215772
		2.4776010337532285e-17 2.4776010337532285e-17 -0.40462295503948226
		-0.28611163533215767 1.7519284920417063e-17 -0.28611163533215767
		;
createNode transform -n "root_ctrl_zero" -p "gr_middle_b_ctrl";
	rename -uid "710277FB-475A-8FBF-1D52-B3B6570F0413";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "root_ctrl_PH" -p "root_ctrl_zero";
	rename -uid "AA7093F0-482A-F4FC-C56A-C3B192388137";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "root_ctrl_SN" -p "root_ctrl_PH";
	rename -uid "EC5AF0E1-41CF-4DE1-278D-DE809F1A00EF";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode transform -n "root_ctrl" -p "root_ctrl_SN";
	rename -uid "3AE9B47A-412E-B72E-9D8A-E8A8BAEDE9C4";
	addAttr -ci true -k true -sn "pivot_vis" -ln "pivot_vis" -min 0 -max 1 -at "long";
	setAttr -l on -k off ".v";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr -k on ".pivot_vis";
createNode nurbsCurve -n "root_ctrlShape" -p "root_ctrl";
	rename -uid "1F626898-4BBD-40C2-CF83-1B8CD907F88F";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 86 0 no 3
		91 15.745750770000001 15.745750770000001 15.745750770000001 15.994336930000005 15.994336930000005 15.994336930000005 16.994336930000003 16.994336930000003 16.994336930000003 17.994336930000003 17.994336930000003
		 17.994336930000003 18.994336930000003 18.994336930000003 18.994336930000003 19.994336930000003 19.994336930000003 19.994336930000003 20.253014204999999 20.253014204999999 20.253014204999999 20.885202119999999 21.502214874
		 21.502214874 21.502214874 21.758286319 21.758286319 21.758286319 22.758286319 22.758286319 22.758286319 23.758286319 23.758286319 23.758286319 24.758286319
		 24.758286319 24.758286319 25.758286319 25.758286319 25.758286319 26.014851714999999 26.014851714999999 26.014851714999999 26.633484611 27.244006168999999 27.244006168999999 27.244006168999999
		 27.495894292999999 27.495894292999999 27.495894292999999 28.495894292999999 28.495894292999999 28.495894292999999 29.495894292999999 29.495894292999999 29.495894292999999 30.495894292999999 30.495894292999999 30.495894292999999
		 31.495894292999999 31.495894292999999 31.495894292999999 31.758026582999999 31.758026582999999 31.758026582999999 32.371381249000002 32.991210664 32.991210664 32.991210664 33.247937673999999 33.247937673999999
		 33.247937673999999 34.247937673999999 34.247937673999999 34.247937673999999 35.247937673999999 35.247937673999999 35.247937673999999 36.247937673999999 36.247937673999999 36.247937673999999 37.247937673999999 37.247937673999999
		 37.247937673999999 37.502186903999998 37.502186903999998 37.502186903999998 38.121090553499997 38.742038981499995 38.742038981499995 38.742038981499995
		89
		0.059003146634936103 -6.6305955526018384e-20 0.19201048959005673
		0.059003146634936103 -1.3578010667232363e-17 0.20667785523995236
		0.059003146634936103 1.3445398756180289e-17 0.22134522088984779
		0.059003146634936103 -6.6305955526018384e-20 0.23601258653974447
		0.078670862179914355 1.3445398756180289e-17 0.23601258653974497
		0.098338577724893295 1.3445398756180289e-17 0.23601258653974497
		0.11800629326987221 -6.8221583113791791e-18 0.23601258653974394
		0.078670862179914355 -2.7089715378938672e-17 0.27534801762970185
		0.039335431089957178 -4.0601420090645141e-17 0.31468344871965742
		5.4096673535576233e-33 1.3445398756180289e-17 0.35401887980961511
		-0.039335431089957178 -4.0601420090645141e-17 0.31468344871965742
		-0.078670862179914355 -5.4113124802351465e-17 0.27534801762970185
		-0.11800629326987221 -6.6305955526018384e-20 0.23601258653974447
		-0.098338577724893295 -6.6305955526018384e-20 0.23601258653974447
		-0.078670862179914355 -3.3845567734791895e-17 0.23601258653974355
		-0.059003146634936103 -6.6305955526018384e-20 0.23601258653974447
		-0.059003146634936103 6.6895464003271374e-18 0.22074981335179214
		-0.059003146634936103 2.6957103467886638e-17 0.20548704016384239
		-0.056983499967470784 2.0201251112033435e-17 0.19187151369753194
		-0.088756897450251102 4.0468808179592885e-17 0.18233354328583742
		-0.14708864042643671 -6.6305955526018384e-20 0.1482117563803334
		-0.18150099756624755 -6.8221583113791791e-18 0.090170583638455482
		-0.1906855234846789 -6.6305955526018384e-20 0.059003146634936117
		-0.2057945445030338 -1.7552690444893118e-18 0.059003146634936082
		-0.22090356552138901 3.3116202224005806e-18 0.059003146634936082
		-0.23601258653974441 -6.6305955526018384e-20 0.059003146634936117
		-0.23601258653974447 -1.0200084489305786e-17 0.078670862179914355
		-0.23601258653974447 -3.4442321334525957e-18 0.098338577724893295
		-0.23601258653974441 6.6895464003271374e-18 0.11800629326987248
		-0.27534801762970185 -2.3711789201012141e-17 0.078670862179914355
		-0.31468344871965742 -6.8221583113791791e-18 0.039335431089957178
		-0.35401887980961511 -8.9228163487269368e-20 3.0926601405221655e-20
		-0.31468344871965742 8.3785094892904349e-18 -0.039335431089957178
		-0.27534801762970185 1.006747257825372e-17 -0.078670862179914355
		-0.23601258653974447 3.3116202224005806e-18 -0.11800629326987197
		-0.23601258653974441 3.3116202224005806e-18 -0.098338577724893295
		-0.23601258653974441 1.006747257825372e-17 -0.078670862179914355
		-0.23601258653974441 -6.6305955526018384e-20 -0.059003146634936117
		-0.22087442085810452 -6.6305955526018384e-20 -0.059003146634936117
		-0.2057362551764669 -3.4442321334525957e-18 -0.059003146634936263
		-0.19124734455420805 -4.3979346268571717e-17 -0.059024156284319854
		-0.18159021906030828 -3.3845567734791895e-17 -0.090019991225068388
		-0.14776060931592594 -4.7357272446498232e-17 -0.14716028796742384
		-0.090773134111573811 -3.3845567734791895e-17 -0.18114271924981057
		-0.059003146634935714 -2.0333863023085463e-17 -0.19142601079183083
		-0.059003146634935714 -6.6305955526018384e-20 -0.20628820270780177
		-0.059003146634935714 6.6895464003271374e-18 -0.22115039462377242
		-0.059003146634935666 -6.6305955526018384e-20 -0.23601258653974447
		-0.078670862179914203 -1.3578010667232363e-17 -0.23601258653974497
		-0.098338577724893281 -1.3578010667232363e-17 -0.23601258653974497
		-0.11800629326987153 -1.3578010667232363e-17 -0.23601258653974497
		-0.078670862179914203 5.3980512891299277e-17 -0.27534801762970185
		-0.039335431089957067 4.0468808179592885e-17 -0.31468344871965742
		-5.4096673535576233e-33 -1.3578010667232363e-17 -0.35401887980961511
		0.039335431089957178 4.0468808179592885e-17 -0.31468344871965742
		0.078670862179914355 5.3980512891299277e-17 -0.27534801762970185
		0.11800629326987221 -6.6305955526018384e-20 -0.23601258653974447
		0.098338577724893295 -6.6305955526018384e-20 -0.23601258653974447
		0.078670862179914355 2.0201251112033435e-17 -0.23601258653974305
		0.059003146634936103 -6.6305955526018384e-20 -0.23601258653974447
		0.059003146634936103 2.0201251112033435e-17 -0.22054595659512224
		0.059003146634936103 -1.3578010667232363e-17 -0.2050793266505008
		0.059817042988123306 -4.0601420090645141e-17 -0.19099854979005215
		0.090510307445715962 -1.3578010667232363e-17 -0.18129925008453052
		0.14773816097810849 6.6895464003271374e-18 -0.1472589638282806
		0.18165605990582265 1.006747257825372e-17 -0.089908722967351973
		0.19056948229120707 -6.6305955526018384e-20 -0.059003146634936117
		0.2057171837073864 1.6226571334372751e-18 -0.059003146634936082
		0.22086488512356409 -3.4442321334525957e-18 -0.059003146634936082
		0.23601258653974441 -6.6305955526018384e-20 -0.059003146634936117
		0.23601258653974447 1.006747257825372e-17 -0.078670862179914355
		0.23601258653974447 3.3116202224005806e-18 -0.098338577724893295
		0.23601258653974441 -6.8221583113791791e-18 -0.11800629326987248
		0.27534801762970185 2.3579177289960055e-17 -0.078670862179914355
		0.31468344871965742 6.6895464003271374e-18 -0.039335431089957178
		0.35401887980961511 -8.9228163487269308e-20 3.0926601405226091e-20
		0.31468344871965742 -6.6305955526018384e-20 0.039335431089957101
		0.27534801762970185 -1.0200084489305786e-17 0.078670862179914355
		0.23601258653974447 -3.4442321334525957e-18 0.11800629326987197
		0.23601258653974441 -3.4442321334525957e-18 0.098338577724893295
		0.23601258653974441 -1.0200084489305786e-17 0.078670862179914355
		0.23601258653974441 -6.6305955526018384e-20 0.059003146634936117
		0.22101108194023406 -6.6305955526018384e-20 0.059003146634936117
		0.20600957734072511 3.3116202224005806e-18 0.059003146634936263
		0.1910080727412147 -6.6305955526018384e-20 0.059003146634936117
		0.18160512165393772 4.3846734357519461e-17 0.089994816803973074
		0.14748623029488339 4.7224660535446099e-17 0.14763756466000436
		0.089804622532273226 5.3980512891299277e-17 0.18171759611247928
		0.058676011860128982 5.3980512891299277e-17 0.19135547409576958
		;
createNode transform -n "root_piv_ctrl" -p "root_ctrl";
	rename -uid "ACA8FFCA-46E2-CFE8-29E2-6CBB43F530A7";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_piv_ctrlShape" -p "root_piv_ctrl";
	rename -uid "3CB0470B-436F-423C-EC19-D993E015E2D0";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20010040159102671 0 0
		;
createNode nurbsCurve -n "root_piv_ctrlShape1" -p "root_piv_ctrl";
	rename -uid "89CCF095-49F8-F7F8-9AD4-5CAC3BB990BA";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20010040159102671 0
		;
createNode nurbsCurve -n "root_piv_ctrlShape2" -p "root_piv_ctrl";
	rename -uid "67A5DD2A-4C07-9C28-884A-B5ABF2C3ECEA";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20010040159102671
		;
createNode transform -n "root_base" -p "root_ctrl";
	rename -uid "4FA2D2B5-434B-C53A-8FB2-2588E0A7F3D1";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "root_ctrl_SN_piv_ctrl" -p "root_ctrl_SN";
	rename -uid "711A6CC0-4995-18D1-7432-27927CF767DE";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape" -p "root_ctrl_SN_piv_ctrl";
	rename -uid "68E724FA-464A-44E0-1956-C78F7D16665A";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20010040159102671 0 0
		;
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape1" -p "root_ctrl_SN_piv_ctrl";
	rename -uid "A644AF38-42CD-C9A8-5070-81BE11FCD085";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20010040159102671 0
		;
createNode nurbsCurve -n "root_ctrl_SN_piv_ctrlShape2" -p "root_ctrl_SN_piv_ctrl";
	rename -uid "E64B827D-46CF-40FA-9073-3D881065CD8B";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20010040159102671
		;
createNode transform -n "root_ctrl_PH_piv_ctrl" -p "root_ctrl_PH";
	rename -uid "4B9BF61E-4905-958B-7909-5989D8E64FA4";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape" -p "root_ctrl_PH_piv_ctrl";
	rename -uid "59342A18-46D6-E748-6033-6E986A24FC45";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20010040159102671 0 0
		;
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape1" -p "root_ctrl_PH_piv_ctrl";
	rename -uid "E3D05E13-4252-57B0-267A-9FBD7283367D";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20010040159102671 0
		;
createNode nurbsCurve -n "root_ctrl_PH_piv_ctrlShape2" -p "root_ctrl_PH_piv_ctrl";
	rename -uid "88CEF1E8-4D1C-60F5-E6C6-2687764B3078";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20010040159102671
		;
createNode transform -n "global_piv_ctrl" -p "global_ctrl";
	rename -uid "90E28268-4292-E776-4D63-3295495E1ED2";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_piv_ctrlShape" -p "global_piv_ctrl";
	rename -uid "C5897255-4B97-F2FE-C23C-58859C51F916";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0.20010040159102671 0 0
		;
createNode nurbsCurve -n "global_piv_ctrlShape1" -p "global_piv_ctrl";
	rename -uid "18160FE3-4C76-BD7B-7F17-0088896C1FE3";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0.20010040159102671 0
		;
createNode nurbsCurve -n "global_piv_ctrlShape2" -p "global_piv_ctrl";
	rename -uid "042D72EE-47AA-4BAA-2D65-9BA1A6D5D74B";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 0.20010040159102671
		;
createNode transform -n "global_ctrl_SN_piv_ctrl" -p "global_ctrl_SN";
	rename -uid "8388E407-4E08-93D6-21DF-00B47A66E254";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape" -p "global_ctrl_SN_piv_ctrl";
	rename -uid "2F18B580-41D2-6876-E258-9FBFFFEAEE92";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		1.1130251222176732 0 0
		;
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape1" -p "global_ctrl_SN_piv_ctrl";
	rename -uid "1FD00DC6-48C9-485E-3D8E-E69DFB433ACF";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 1.1130251222176732 0
		;
createNode nurbsCurve -n "global_ctrl_SN_piv_ctrlShape2" -p "global_ctrl_SN_piv_ctrl";
	rename -uid "349CAAB2-4299-DFD8-8665-489B6FC9D6E2";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 1.1130251222176732
		;
createNode transform -n "global_ctrl_PH_piv_ctrl" -p "global_ctrl_PH";
	rename -uid "06F9BD94-4994-8324-5683-32AE7E92BEBD";
	setAttr -k off ".v";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape" -p "global_ctrl_PH_piv_ctrl";
	rename -uid "761A27AE-4444-8AC1-9EFD-B3977960B0EF";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		1.1130251222176732 0 0
		;
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape1" -p "global_ctrl_PH_piv_ctrl";
	rename -uid "AAAC1CA8-401E-925D-795A-C1BF708F6E51";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 1.1130251222176732 0
		;
createNode nurbsCurve -n "global_ctrl_PH_piv_ctrlShape2" -p "global_ctrl_PH_piv_ctrl";
	rename -uid "3511F4C3-4625-AE8F-9169-77B7963A673E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 0 0
		0 0 1.1130251222176732
		;
createNode transform -n "anim_skeletons_grp" -p "anim_rig";
	rename -uid "9BA8B50C-4CB7-F601-5BAB-EF8A1C914E4D";
	setAttr ".it" no;
lockNode -l 1 ;
createNode transform -n "anim_modules_grp" -p "anim_rig";
	rename -uid "5466AD32-48DF-7FAE-E351-20B4FB2EEE46";
	setAttr ".it" no;
lockNode -l 1 ;
createNode transform -s -n "persp";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A0";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0.87824346825400246 1.608238647798319 1.4541328822439736 ;
	setAttr ".r" -type "double3" -42.938352729606201 31.400000000000642 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A1";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 2.3571980959412588;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A2";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -0.041391120841696494 1000.1 0.1806158000364938 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A3";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 11.245678105715312;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A4";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A5";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A6";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "DF5849C0-0000-17E7-69DD-B024000004A7";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "662679C0-0001-D20A-69F1-C80600000345";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "662679C0-0001-D20A-69F1-C80600000346";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "662679C0-0001-D20A-69F1-C80600000347";
createNode displayLayerManager -n "layerManager";
	rename -uid "662679C0-0001-D20A-69F1-C80600000348";
createNode displayLayer -n "defaultLayer";
	rename -uid "DF5849C0-0000-17E7-69DD-B025000004AC";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "662679C0-0001-D20A-69F1-C8060000034A";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "DF5849C0-0000-17E7-69DD-B025000004AE";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "DF5849C0-0000-17E7-69DD-B03E000004AF";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "EAF159C0-0001-2F40-69DF-5D1500000699";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -533.86522701305216 -439.28569683006901 ;
	setAttr ".tgi[0].vh" -type "double2" 507.67475186329204 84.523806165135213 ;
	setAttr -s 4 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 208.57142639160156;
	setAttr ".tgi[0].ni[0].y" -21.428571701049805;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" -99.579010009765625;
	setAttr ".tgi[0].ni[1].y" 105.71428680419922;
	setAttr ".tgi[0].ni[1].nvs" 18306;
	setAttr ".tgi[0].ni[2].x" 208.57142639160156;
	setAttr ".tgi[0].ni[2].y" 105.71428680419922;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" -405.71429443359375;
	setAttr ".tgi[0].ni[3].y" 105.71428680419922;
	setAttr ".tgi[0].ni[3].nvs" 18306;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 1;
	setAttr -av -k on ".unw" 1;
	setAttr -av -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
lockNode -l 0 -lu 1;
select -ne :sequenceManager1;
	setAttr ".o" 633;
select -ne :hardwareRenderingGlobals;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".fzn";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".rm";
	setAttr -av -k on ".lm";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr -av -k on ".hom";
	setAttr -av -k on ".hodm";
	setAttr -av -k on ".xry";
	setAttr -av -k on ".jxr";
	setAttr -av -k on ".sslt";
	setAttr -av -k on ".cbr";
	setAttr -av -k on ".bbr";
	setAttr -av -k on ".mhl";
	setAttr -av -k on ".cons";
	setAttr -av -k on ".vac";
	setAttr -av -k on ".hwi";
	setAttr -av -k on ".csvd";
	setAttr -av -k on ".ta";
	setAttr -av -k on ".tq";
	setAttr -av -k on ".ts";
	setAttr -av -k on ".etmr";
	setAttr -k on ".tmrm";
	setAttr -av -k on ".tmr";
	setAttr -av -k on ".aoon";
	setAttr -av -k on ".aoam";
	setAttr -av -k on ".aora";
	setAttr -av -k on ".aofr";
	setAttr -av -k on ".aosm";
	setAttr -av -k on ".hff";
	setAttr -av -k on ".hfd";
	setAttr -av -k on ".hfs" 33.783782958984375;
	setAttr -av -k on ".hfe" 260.1351318359375;
	setAttr -av ".hfc" -type "float3" 0.67900002 0.83318162 1 ;
	setAttr -av ".hfc";
	setAttr -av -k on ".hfcr";
	setAttr -av -k on ".hfcg";
	setAttr -av -k on ".hfcb";
	setAttr -av -k on ".hfa" 0.11486486345529556;
	setAttr -av -k on ".mbe";
	setAttr -av -k on ".mbt";
	setAttr -av -k on ".mbsof";
	setAttr -av -k on ".mbsc";
	setAttr -av -k on ".mbc";
	setAttr -av -k on ".mbfa";
	setAttr -av -k on ".mbftb";
	setAttr -av -k on ".mbftg";
	setAttr -av -k on ".mbftr";
	setAttr -av -k on ".mbfta";
	setAttr -av -k on ".mbfe";
	setAttr -av -k on ".mbme";
	setAttr -av -k on ".mbcsx";
	setAttr -av -k on ".mbcsy";
	setAttr -av -k on ".mbasx";
	setAttr -av -k on ".mbasy";
	setAttr -av -k on ".blen";
	setAttr -av -k on ".blth";
	setAttr -av -k on ".blfr";
	setAttr -av -k on ".blfa";
	setAttr -av -k on ".blat";
	setAttr -av -k on ".msaa" yes;
	setAttr -av -k on ".aasc";
	setAttr -av -k on ".aasq";
	setAttr -av -k on ".laa";
	setAttr -k on ".gamm";
	setAttr -k on ".gmmv";
	setAttr -k on ".fprt" yes;
	setAttr -av -k on ".rtfm";
select -ne :renderPartition;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
lockNode -l 0 -lu 1;
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -av -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -k on ".hio";
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -k on ".mwc";
	setAttr -av -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -k on ".hio";
lockNode -l 0 -lu 1;
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w" 2048;
	setAttr -av -k on ".h" 858;
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar" 2.3870000839233398;
	setAttr -av -k on ".ldar";
	setAttr -av -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -k on ".isu";
	setAttr -av -k on ".pdu";
select -ne :hardwareRenderGlobals;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k off -cb on ".ctrs" 256;
	setAttr -av -k off -cb on ".btrs" 512;
	setAttr -av -k off -cb on ".fbfm";
	setAttr -av -k off -cb on ".ehql";
	setAttr -av -k off -cb on ".eams";
	setAttr -av -k off -cb on ".eeaa";
	setAttr -av -k off -cb on ".engm";
	setAttr -av -k off -cb on ".mes";
	setAttr -av -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -av -k off -cb on ".mbs";
	setAttr -av -k off -cb on ".trm";
	setAttr -av -k off -cb on ".tshc";
	setAttr -av -k off -cb on ".enpt";
	setAttr -av -k off -cb on ".clmt";
	setAttr -av -k off -cb on ".tcov";
	setAttr -av -k off -cb on ".lith";
	setAttr -av -k off -cb on ".sobc";
	setAttr -av -k off -cb on ".cuth";
	setAttr -av -k off -cb on ".hgcd";
	setAttr -av -k off -cb on ".hgci";
	setAttr -av -k off -cb on ".mgcs";
	setAttr -av -k off -cb on ".twa";
	setAttr -av -k off -cb on ".twz";
	setAttr -av -k on ".hwcc";
	setAttr -av -k on ".hwdp";
	setAttr -av -k on ".hwql";
	setAttr -av -k on ".hwfr";
	setAttr -av -k on ".soll";
	setAttr -av -k on ".sosl";
	setAttr -av -k on ".bswa";
	setAttr -av -k on ".shml";
	setAttr -av -k on ".hwel";
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
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "root_ctrlShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn";
connectAttr "root_ctrl.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "root_piv_ctrl.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn";
connectAttr "global_ctrl.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
dataStructure -fmt "raw" -as "name=notes_concretesGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_tunnel:string=value";
dataStructure -fmt "raw" -as "name=mapManager_restaurantFront:string=value";
dataStructure -fmt "raw" -as "name=FBXFastExportSetting_MB:string=19424";
dataStructure -fmt "raw" -as "name=notes_barbacueHouseFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassA_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_floorConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_vgFCarouselBed_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_original:string=value";
dataStructure -fmt "raw" -as "name=notes_floor1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassB_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundWoods_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayMain_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_heroesChoice_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_base_hojas:string=value";
dataStructure -fmt "raw" -as "name=mapManager_det:string=value";
dataStructure -fmt "raw" -as "name=mapManager_square_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassBase:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsRight:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket_flowers:string=value";
dataStructure -fmt "raw" -as "name=mapManager_throwbotLeft_scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksGrounds:string=value";
dataStructure -fmt "raw" -as "name=notes_mainStreetMainstreetTrees04:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloP1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_leaves:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassD_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesMountainsGrass_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_grassJuneBackYard_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeaves_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloP1:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiary:string=value";
dataStructure -fmt "raw" -as "name=wingnut_ar:string=metadata";
dataStructure -fmt "raw" -as "name=notes_floorOrangeConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseForest:string=value";
dataStructure -fmt "raw" -as "name=mapManager_strap_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantNextHouse_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_levelC:string=value";
dataStructure -fmt "raw" -as "name=notes_squareRocks_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_base_right:string=value";
dataStructure -fmt "raw" -as "name=notes_baseScatter:string=value";
dataStructure -fmt "raw" -as "name=mapManager_railes:string=value";
dataStructure -fmt "raw" -as "name=DiffEdge:float=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSA:string=value";
dataStructure -fmt "raw" -as "name=notes_road_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grasses:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesTrees_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_circular:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseScatter:string=value";
dataStructure -fmt "raw" -as "name=notes_vgTFicus39:string=value";
dataStructure -fmt "raw" -as "name=notes_ground_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassD_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwaySquareFlowers_parShape:string=value";
dataStructure -fmt "raw" -as "name=OffStruct:float=Offset";
dataStructure -fmt "raw" -as "name=notes_grass_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_groundWoods_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_hojas:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayCircular_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesGrasStairs_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_frogEntrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorA:string=value";
dataStructure -fmt "raw" -as "name=notes_rocskLeftPLA:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksCurbsGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayFlowerBeds_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesGrassDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA9:string=value";
dataStructure -fmt "raw" -as "name=notes_leaves_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_road_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassD_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassD_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_polySurface56:string=value";
dataStructure -fmt "raw" -as "name=mapManager_original:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_left:string=value";
dataStructure -fmt "raw" -as "name=notes_floorScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_concretePath_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_grass:string=value";
dataStructure -fmt "raw" -as "name=notes_bushesA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_curbsGardenGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_terracesSuelo:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_new_sand:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA8:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees:string=value";
dataStructure -fmt "raw" -as "name=notes_fountainHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_tunnel:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_Scatt:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaCorner_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_riverSideground:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchDegraded_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_chocolateFountain_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiaryGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_treesRocksHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=FameDataStructure:string=value";
dataStructure -fmt "raw" -as "name=IdStruct:int32=ID";
dataStructure -fmt "raw" -as "name=mapManager_stairs_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1A:string=value";
dataStructure -fmt "raw" -as "name=notes_sidewalkGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorOrangeConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassC_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA8:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksGround:string=value";
dataStructure -fmt "raw" -as "name=fw_animation_file:bool=True";
dataStructure -fmt "raw" -as "name=notes_slopesC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane3:string=value";
dataStructure -fmt "raw" -as "name=mapManager_degraded:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloA:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchF_parShape:string=value";
dataStructure -fmt "raw" -as "name=OrgStruct:float[3]=Origin Point";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined2:string=value";
dataStructure -fmt "raw" -as "name=notes_trees:string=value";
dataStructure -fmt "raw" -as "name=notes_terraces_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_hotelBack_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_left:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base_right:string=value";
dataStructure -fmt "raw" -as "name=notes_riverside_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayMain_Flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_base_left:string=value";
dataStructure -fmt "raw" -as "name=mapManager_curbsGarden_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_rocks:string=value";
dataStructure -fmt "raw" -as "name=Curvature:float=mean:float=gaussian:float=ABS:float=RMS";
dataStructure -fmt "raw" -as "name=mapManager_floorConcrete_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_mountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_amp_lyref_cmp0010_layGround:string=value";
dataStructure -fmt "raw" -as "name=notes_floorCampfire:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyFlowersBedA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_small:string=value";
dataStructure -fmt "raw" -as "name=idStructure:int32=ID";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSA:string=value";
dataStructure -fmt "raw" -as "name=ColorStruct:float[3]=Color:int32=ID";
dataStructure -fmt "raw" -as "name=TifLocation:string=Path";
dataStructure -fmt "raw" -as "name=notes_bridge_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeavesCarousel_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_big_back:string=value";
dataStructure -fmt "raw" -as "name=notes_ground03_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorCampfire:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined2:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_left1:string=value";
dataStructure -fmt "raw" -as "name=notes_treesRocksAnimalHome_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayArea_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantBack_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloB:string=value";
dataStructure -fmt "raw" -as "name=mapManager_base:string=value";
dataStructure -fmt "raw" -as "name=notes_terraceBush_parShape:string=value";
dataStructure -fmt "raw" -as "name=Blur3dMetaData:string=Blur3dValue";
dataStructure -fmt "raw" -as "name=notes_floorFlower:string=value";
dataStructure -fmt "raw" -as "name=mapManager_drawBridge_physPivot:string=value";
dataStructure -fmt "raw" -as "name=mapManager_geos:string=value";
dataStructure -fmt "raw" -as "name=notes_vgtCampfire_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloP2:string=value";
dataStructure -fmt "raw" -as "name=notes_base:string=value";
dataStructure -fmt "raw" -as "name=notes_grassD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_det:string=value";
dataStructure -fmt "raw" -as "name=notes_grassC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_ridePiggy_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_baseScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_big_back:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA9:string=value";
dataStructure -fmt "raw" -as "name=notes_decayLeavesFlowerBed_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floorOrangeGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayRocket_flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_strap_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloA:string=value";
dataStructure -fmt "raw" -as "name=notes_leavesDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayAreaD_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesFlowers_parShape:string=value";
dataStructure -fmt "raw" -as "name=ComboStructure:bool=shape";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassC_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_backgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_grassRightMountains:string=value";
dataStructure -fmt "raw" -as "name=notes_scatt:string=value";
dataStructure -fmt "raw" -as "name=notes_square_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_floor_flowers:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=f_3:float[3]=value";
dataStructure -fmt "raw" -as "name=notes_frogLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_suelofuente:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloor_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_baseForest:string=value";
dataStructure -fmt "raw" -as "name=notes_rightExterior_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_railes:string=value";
dataStructure -fmt "raw" -as "name=BilateralStructure:bool=right:bool=center:bool=left";
dataStructure -fmt "raw" -as "name=notes_sueloP2:string=value";
dataStructure -fmt "raw" -as "name=notes_base_parShape:string=value";
dataStructure -fmt "raw" -as "name=faceConnectMarkerStructure:bool=faceConnectMarker:string[200]=faceConnectOutputGroups";
dataStructure -fmt "raw" -as "name=notes_bricksGrounds:string=value";
dataStructure -fmt "raw" -as "name=notes_center_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_riverSide:string=value";
dataStructure -fmt "raw" -as "name=keyValueStructure:string=value";
dataStructure -fmt "raw" -as "name=notes_juneNbhHouseE_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_leaves:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sand_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_cheat_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane4:string=value";
dataStructure -fmt "raw" -as "name=notes_rockSignRollo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_slopes:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rocskLeftPLA:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksGround:string=value";
dataStructure -fmt "raw" -as "name=notes_level1A:string=value";
dataStructure -fmt "raw" -as "name=notes_degraded:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBeauty_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassADecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_amp_lyref_cmp0010_layGround:string=value";
dataStructure -fmt "raw" -as "name=mapManager_tilesFloorDet:string=value";
dataStructure -fmt "raw" -as "name=notes_level1B_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_path:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundRocks:string=value";
dataStructure -fmt "raw" -as "name=notes_rockTerraces_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTielMainStreet_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchH_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloor:string=value";
dataStructure -fmt "raw" -as "name=mapManager_suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_tilesFloorDet:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane5:string=value";
dataStructure -fmt "raw" -as "name=notes_square_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersRightLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_background_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_vgGroundB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTopiary:string=value";
dataStructure -fmt "raw" -as "name=notes_terraceGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseLeaves:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slideSundaeRightScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassRightMountains:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_CombinedGrass:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainTrail_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwaySpaceland_Main_Leaves:string=value";
dataStructure -fmt "raw" -as "name=notes_slopes_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayRocket:string=value";
dataStructure -fmt "raw" -as "name=mapManager_flowersSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchC_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwaySquare_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesGroundGrassA_Combined:string=value";
dataStructure -fmt "raw" -as "name=Offset:float[3]=value";
dataStructure -fmt "raw" -as "name=notes_Suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_groundC_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_groundPlane_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassCenter_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksTopiary_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_treesB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassRightMountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floor_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSB:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsCSB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_wasteLand_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_polySurface56:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_c_geo1:string=value";
dataStructure -fmt "raw" -as "name=notes_curbsGarden_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1B_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_throwbotLeft_scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorFlower:string=value";
dataStructure -fmt "raw" -as "name=LauncherVersion:string=Version";
dataStructure -fmt "raw" -as "name=notes_mountainsCSA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_centerStreetGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesSuelo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSC:string=value";
dataStructure -fmt "raw" -as "name=notes_juneBackYard:string=value";
dataStructure -fmt "raw" -as "name=notes_left_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floorGrassA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_square_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_square_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_ferns_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_bricksFence_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_baseLeaves:string=value";
dataStructure -fmt "raw" -as "name=notes_grassDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_railwayGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_circular:string=value";
dataStructure -fmt "raw" -as "name=FBXFastExportSetting_FBX:string=54";
dataStructure -fmt "raw" -as "name=notes_throwbotLeftScatt:string=value";
dataStructure -fmt "raw" -as "name=faceConnectOutputStructure:bool=faceConnectOutput:string[200]=faceConnectOutputAttributes:string[200]=faceConnectOutputGroups";
dataStructure -fmt "raw" -as "name=notes_treesA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_groundRocks:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeRightScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoB_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_restaurantBack:string=value";
dataStructure -fmt "raw" -as "name=notes_scatterGround:string=value";
dataStructure -fmt "raw" -as "name=notes_groundD_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_holeRock_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane2:string=value";
dataStructure -fmt "raw" -as "name=notes_small_grass:string=value";
dataStructure -fmt "raw" -as "name=f_1:float=value";
dataStructure -fmt "raw" -as "name=notes_flowersSquare:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchD_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_walkwayMain_Flowers:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rocks:string=value";
dataStructure -fmt "raw" -as "name=mapManager_baseScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersMain_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_treesRocksrenderalHome_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_road_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_level1A_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchE_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainsCSC_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees_left:string=value";
dataStructure -fmt "raw" -as "name=mapManager_scatterGround:string=value";
dataStructure -fmt "raw" -as "name=mapManager_midgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_rockSignRollo_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloC:string=value";
dataStructure -fmt "raw" -as "name=notes_suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_stoneFloorGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor_flowers:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane2:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground03_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_riverSide:string=value";
dataStructure -fmt "raw" -as "name=notes_groundA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_Suelo:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloC:string=value";
dataStructure -fmt "raw" -as "name=notes_concretePath_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_grassCDecay_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopesGroundGrassB_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_sand_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grass_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTopiary_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane1:string=value";
dataStructure -fmt "raw" -as "name=notes_carouselStairs_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_vegetation_parShape:string=value";
dataStructure -fmt "raw" -as "name=RenderSettings:string=preset";
dataStructure -fmt "raw" -as "name=mapManager_juneBackYard:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floor1:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane5:string=value";
dataStructure -fmt "raw" -as "name=notes_midground_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_frogL_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_groundPlane_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchG_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slideSundaeLeft_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_sueloB:string=value";
dataStructure -fmt "raw" -as "name=notes_slabsAndStairsGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_levelUnoA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_leftSpecific_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_Combined1:string=value";
dataStructure -fmt "raw" -as "name=notes_grassCampfire_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_riverSideground:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantFront:string=value";
dataStructure -fmt "raw" -as "name=notes_drawBridge_physPivot:string=value";
dataStructure -fmt "raw" -as "name=notes_groundB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_backgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_beautyGrassPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_grassGround_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_level1A_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_flowersHA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksFence_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_rockCheated_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_levelC:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesMountainsGrass_Combined:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane3:string=value";
dataStructure -fmt "raw" -as "name=DiffArea:float=value";
dataStructure -fmt "raw" -as "name=notes_geos:string=value";
dataStructure -fmt "raw" -as "name=notes_testMode_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_pPlane6:string=value";
dataStructure -fmt "raw" -as "name=notes_grassBase:string=value";
dataStructure -fmt "raw" -as "name=mapManager_backWall_c_geo:string=value";
dataStructure -fmt "raw" -as "name=notes_fountainRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_floorScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_CombinedGrass:string=value";
dataStructure -fmt "raw" -as "name=notes_snapshot_floor:string=value";
dataStructure -fmt "raw" -as "name=notes_bricksTielMainStreet_c_geo:string=value";
dataStructure -fmt "raw" -as "name=externalContentTablZ:string=nodZ:string=key:string=upath:uint32=upathcrc:string=rpath:string=roles";
dataStructure -fmt "raw" -as "name=notes_widlPatchB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_terracesRight_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_wildPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_slopesCDetail_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_throwbotLeftScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_sueloProvi3:string=value";
dataStructure -fmt "raw" -as "name=notes_tunnelParkEntrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_stoneFloor:string=value";
dataStructure -fmt "raw" -as "name=notes_trees_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grass_Scatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground:string=value";
dataStructure -fmt "raw" -as "name=notes_grasses:string=value";
dataStructure -fmt "raw" -as "name=notes_midgroundPlane:string=value";
dataStructure -fmt "raw" -as "name=notes_stairs_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_rockSignRollo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane4:string=value";
dataStructure -fmt "raw" -as "name=mapManager_small:string=value";
dataStructure -fmt "raw" -as "name=NameAndID:string=name:int32=ID";
dataStructure -fmt "raw" -as "name=notes_terracesGrass_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_bushes_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_grassLeftMountains_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_ground_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_slopes:string=value";
dataStructure -fmt "raw" -as "name=mapManager_arbustosScatt:string=value";
dataStructure -fmt "raw" -as "name=notes_arbustosScatt:string=value";
dataStructure -fmt "raw" -as "name=mapManager_grassGround_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane1:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantFront_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwaySpaceland_Main_Leaves:string=value";
dataStructure -fmt "raw" -as "name=notes_restaurantBack:string=value";
dataStructure -fmt "raw" -as "name=notes_suelofuente:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassPatchA_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_pPlane6:string=value";
dataStructure -fmt "raw" -as "name=mapManager_small_grass:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainCSB:string=value";
dataStructure -fmt "raw" -as "name=notes_walkwayRocket:string=value";
dataStructure -fmt "raw" -as "name=mapManager_snapshot_Combined:string=value";
dataStructure -fmt "raw" -as "name=notes_backWall_c_geo:string=value";
dataStructure -fmt "raw" -as "name=mapManager_trees_left1:string=value";
dataStructure -fmt "raw" -as "name=notes_decayGrassesCenter_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_entrance_parShape:string=value";
dataStructure -fmt "raw" -as "name=mapManager_mountainsRight:string=value";
dataStructure -fmt "raw" -as "name=notes_path:string=value";
dataStructure -fmt "raw" -as "name=notes_right_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_floorA:string=value";
dataStructure -fmt "raw" -as "name=notes_new_sand:string=value";
dataStructure -fmt "raw" -as "name=notes_sidewalkGrassB_parShape:string=value";
dataStructure -fmt "raw" -as "name=notes_mountainCSC:string=value";
dataStructure -fmt "raw" -as "name=notes_floorSquare:string=value";
applyMetadata -fmt "raw" -v "channel\nname default\nstream\nname wingnut_ar_stream\nindexType string\nstructure wingnut_ar\ncontext\n\"S'MKT-Master-1.0.1'\\np0\\n.\"\ncontext_resolve\n\"(lp0\\nS'maya_common_fishbowl-0.1.0'\\np1\\naS'platform-windows'\\np2\\naS'arch-AMD64'\\np3\\naS'autodesk_license-1.0.0'\\np4\\naS'maya-2019.2.0'\\np5\\naS'maya_live_link-2.0'\\np6\\naS'mgear-3.1.1'\\np7\\naS'mtoa-2019.2.0'\\np8\\naS'chaosgroup_license-1.0.0'\\np9\\naS'vray_for_maya-4.12.1.1'\\np10\\naS'six-1.10.0'\\np11\\naS'anytree-2.2.2'\\np12\\naS'python-2.7.14'\\np13\\naS'p4python-2017.2.1615960'\\np14\\naS'functools32-3.2.3.post2'\\np15\\naS'jsonschema-2.6.0'\\np16\\naS'rez_api-2.47.2'\\np17\\naS'qt_py-1.2.2'\\np18\\naS'war_qt-1.4.0'\\np19\\naS'shotgun_api3-3.0.40'\\np20\\naS'war-1.0.0'\\np21\\naS'ffmpeg-4.0.2'\\np22\\naS'enum34-1.1.6'\\np23\\naS'future-0.16.0'\\np24\\naS'ffmpeg_python-0.2.0'\\np25\\naS'requests-2.14.2'\\np26\\naS'war_foundations-2.36.1'\\np27\\naS'war_menu-1.4.1'\\np28\\naS'war_assets-2.4.0'\\np29\\naS'war_unreal-1.3.3'\\np30\\naS'war_scene-4.4.0'\\np31\\naS'war_machine-1.0.5'\\np32\\naS'war_anim-1.0.6'\\np33\\naS'war_compass-0.3.0'\\np34\\naS'war_maya_blendshapeRecv-2.1.1'\\np35\\naS'war_maya-1.0.0'\\np36\\naS'war_maya_common-1.7.1'\\np37\\naS'docutils-0.14'\\np38\\naS'wmPolyGoodies-4.04.1'\\np39\\naS'war_maya_validation-4.6.1'\\np40\\naS'war_ocio-2.5.1'\\np41\\naS'rv-7.3.1'\\np42\\naS'war_scene_maya-4.2.0'\\np43\\naS'wmModels-1.8.1'\\np44\\naS'wmMisc-6.17.1'\\np45\\naS'wmVertCopy-2.6.1'\\np46\\naS'AsfAmc-0.33.11'\\np47\\naS'wmAnim-1.51.2'\\np48\\naS'weta_cre-1.2.1'\\np49\\naS'weta_maya_models-0.2.0'\\np50\\na.\"\ncontext_rxt\n\"(dp0\\nVrez_version\\np1\\nV2.47.2\\np2\\nsVresolved_packages\\np3\\n(lp4\\n(dp5\\nVvariables\\np6\\n(dp7\\nVindex\\np8\\nNsVversion\\np9\\nV0.1.0\\np10\\nsVrepository_type\\np11\\nVfilesystem\\np12\\nsVlocation\\np13\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np14\\nsVname\\np15\\nVmaya_common_fishbowl\\np16\\nssVkey\\np17\\nVfilesystem.variant\\np18\\nsa(dp19\\nVvariables\\np20\\n(dp21\\nVindex\\np22\\nNsVversion\\np23\\nVwindows\\np24\\nsVrepository_type\\np25\\nVfilesystem\\np26\\nsVlocation\\np27\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np28\\nsVname\\np29\\nVplatform\\np30\\nssVkey\\np31\\nVfilesystem.variant\\np32\\nsa(dp33\\nVvariables\\np34\\n(dp35\\nVindex\\np36\\nNsVversion\\np37\\nVAMD64\\np38\\nsVrepository_type\\np39\\nVfilesystem\\np40\\nsVlocation\\np41\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np42\\nsVname\\np43\\nVarch\\np44\\nssVkey\\np45\\nVfilesystem.variant\\np46\\nsa(dp47\\nVvariables\\np48\\n(dp49\\nVindex\\np50\\nNsVversion\\np51\\nV1.0.0\\np52\\nsVrepository_type\\np53\\nVfilesystem\\np54\\nsVlocation\\np55\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np56\\nsVname\\np57\\nVautodesk_license\\np58\\nssVkey\\np59\\nVfilesystem.variant\\np60\\nsa(dp61\\nVvariables\\np62\\n(dp63\\nVindex\\np64\\nI0\\nsVversion\\np65\\nV2019.2.0\\np66\\nsVrepository_type\\np67\\nVfilesystem\\np68\\nsVlocation\\np69\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np70\\nsVname\\np71\\nVmaya\\np72\\nssVkey\\np73\\nVfilesystem.variant\\np74\\nsa(dp75\\nVvariables\\np76\\n(dp77\\nVindex\\np78\\nI3\\nsVversion\\np79\\nV2.0\\np80\\nsVrepository_type\\np81\\nVfilesystem\\np82\\nsVlocation\\np83\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np84\\nsVname\\np85\\nVmaya_live_link\\np86\\nssVkey\\np87\\nVfilesystem.variant\\np88\\nsa(dp89\\nVvariables\\np90\\n(dp91\\nVindex\\np92\\nI0\\nsVversion\\np93\\nV3.1.1\\np94\\nsVrepository_type\\np95\\nVfilesystem\\np96\\nsVlocation\\np97\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np98\\nsVname\\np99\\nVmgear\\np100\\nssVkey\\np101\\nVfilesystem.variant\\np102\\nsa(dp103\\nVvariables\\np104\\n(dp105\\nVindex\\np106\\nI0\\nsVversion\\np107\\nV2019.2.0\\np108\\nsVrepository_type\\np109\\nVfilesystem\\np110\\nsVlocation\\np111\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np112\\nsVname\\np113\\nVmtoa\\np114\\nssVkey\\np115\\nVfilesystem.variant\\np116\\nsa(dp117\\nVvariables\\np118\\n(dp119\\nVindex\\np120\\nNsVversion\\np121\\nV1.0.0\\np122\\nsVrepository_type\\np123\\nVfilesystem\\np124\\nsVlocation\\np125\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np126\\nsVname\\np127\\nVchaosgroup_license\\np128\\nssVkey\\np129\\nVfilesystem.variant\\np130\\nsa(dp131\\nVvariables\\np132\\n(dp133\\nVindex\\np134\\nI0\\nsVversion\\np135\\nV4.12.1.1\\np136\\nsVrepository_type\\np137\\nVfilesystem\\np138\\nsVlocation\\np139\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np140\\nsVname\\np141\\nVvray_for_maya\\np142\\nssVkey\\np143\\nVfilesystem.variant\\np144\\nsa(dp145\\nVvariables\\np146\\n(dp147\\nVindex\\np148\\nNsVversion\\np149\\nV1.10.0\\np150\\nsVrepository_type\\np151\\nVfilesystem\\np152\\nsVlocation\\np153\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np154\\nsVname\\np155\\nVsix\\np156\\nssVkey\\np157\\nVfilesystem.variant\\np158\\nsa(dp159\\nVvariables\\np160\\n(dp161\\nVindex\\np162\\nNsVversion\\np163\\nV2.2.2\\np164\\nsVrepository_type\\np165\\nVfilesystem\\np166\\nsVlocation\\np167\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np168\\nsVname\\np169\\nVanytree\\np170\\nssVkey\\np171\\nVfilesystem.variant\\np172\\nsa(dp173\\nVvariables\\np174\\n(dp175\\nVindex\\np176\\nNsVversion\\np177\\nV2.7.14\\np178\\nsVrepository_type\\np179\\nVfilesystem\\np180\\nsVlocation\\np181\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np182\\nsVname\\np183\\nVpython\\np184\\nssVkey\\np185\\nVfilesystem.variant\\np186\\nsa(dp187\\nVvariables\\np188\\n(dp189\\nVindex\\np190\\nI0\\nsVversion\\np191\\nV2017.2.1615960\\np192\\nsVrepository_type\\np193\\nVfilesystem\\np194\\nsVlocation\\np195\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np196\\nsVname\\np197\\nVp4python\\np198\\nssVkey\\np199\\nVfilesystem.variant\\np200\\nsa(dp201\\nVvariables\\np202\\n(dp203\\nVindex\\np204\\nNsVversion\\np205\\nV3.2.3.post2\\np206\\nsVrepository_type\\np207\\nVfilesystem\\np208\\nsVlocation\\np209\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np210\\nsVname\\np211\\nVfunctools32\\np212\\nssVkey\\np213\\nVfilesystem.variant\\np214\\nsa(dp215\\nVvariables\\np216\\n(dp217\\nVindex\\np218\\nI0\\nsVversion\\np219\\nV2.6.0\\np220\\nsVrepository_type\\np221\\nVfilesystem\\np222\\nsVlocation\\np223\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np224\\nsVname\\np225\\nVjsonschema\\np226\\nssVkey\\np227\\nVfilesystem.variant\\np228\\nsa(dp229\\nVvariables\\np230\\n(dp231\\nVindex\\np232\\nI0\\nsVversion\\np233\\nV2.47.2\\np234\\nsVrepository_type\\np235\\nVfilesystem\\np236\\nsVlocation\\np237\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np238\\nsVname\\np239\\nVrez_api\\np240\\nssVkey\\np241\\nVfilesystem.variant\\np242\\nsa(dp243\\nVvariables\\np244\\n(dp245\\nVindex\\np246\\nNsVversion\\np247\\nV1.2.2\\np248\\nsVrepository_type\\np249\\nVfilesystem\\np250\\nsVlocation\\np251\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np252\\nsVname\\np253\\nVqt_py\\np254\\nssVkey\\np255\\nVfilesystem.variant\\np256\\nsa(dp257\\nVvariables\\np258\\n(dp259\\nVindex\\np260\\nNsVversion\\np261\\nV1.4.0\\np262\\nsVrepository_type\\np263\\nVfilesystem\\np264\\nsVlocation\\np265\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np266\\nsVname\\np267\\nVwar_qt\\np268\\nssVkey\\np269\\nVfilesystem.variant\\np270\\nsa(dp271\\nVvariables\\np272\\n(dp273\\nVindex\\np274\\nNsVversion\\np275\\nV3.0.40\\np276\\nsVrepository_type\\np277\\nVfilesystem\\np278\\nsVlocation\\np279\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np280\\nsVname\\np281\\nVshotgun_api3\\np282\\nssVkey\\np283\\nVfilesystem.variant\\np284\\nsa(dp285\\nVvariables\\np286\\n(dp287\\nVindex\\np288\\nNsVversion\\np289\\nV1.0.0\\np290\\nsVrepository_type\\np291\\nVfilesystem\\np292\\nsVlocation\\np293\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np294\\nsVname\\np295\\nVwar\\np296\\nssVkey\\np297\\nVfilesystem.variant\\np298\\nsa(dp299\\nVvariables\\np300\\n(dp301\\nVindex\\np302\\nI0\\nsVversion\\np303\\nV4.0.2\\np304\\nsVrepository_type\\np305\\nVfilesystem\\np306\\nsVlocation\\np307\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np308\\nsVname\\np309\\nVffmpeg\\np310\\nssVkey\\np311\\nVfilesystem.variant\\np312\\nsa(dp313\\nVvariables\\np314\\n(dp315\\nVindex\\np316\\nNsVversion\\np317\\nV1.1.6\\np318\\nsVrepository_type\\np319\\nVfilesystem\\np320\\nsVlocation\\np321\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np322\\nsVname\\np323\\nVenum34\\np324\\nssVkey\\np325\\nVfilesystem.variant\\np326\\nsa(dp327\\nVvariables\\np328\\n(dp329\\nVindex\\np330\\nI0\\nsVversion\\np331\\nV0.16.0\\np332\\nsVrepository_type\\np333\\nVfilesystem\\np334\\nsVlocation\\np335\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np336\\nsVname\\np337\\nVfuture\\np338\\nssVkey\\np339\\nVfilesystem.variant\\np340\\nsa(dp341\\nVvariables\\np342\\n(dp343\\nVindex\\np344\\nNsVversion\\np345\\nV0.2.0\\np346\\nsVrepository_type\\np347\\nVfilesystem\\np348\\nsVlocation\\np349\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np350\\nsVname\\np351\\nVffmpeg_python\\np352\\nssVkey\\np353\\nVfilesystem.variant\\np354\\nsa(dp355\\nVvariables\\np356\\n(dp357\\nVindex\\np358\\nNsVversion\\np359\\nV2.14.2\\np360\\nsVrepository_type\\np361\\nVfilesystem\\np362\\nsVlocation\\np363\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np364\\nsVname\\np365\\nVrequests\\np366\\nssVkey\\np367\\nVfilesystem.variant\\np368\\nsa(dp369\\nVvariables\\np370\\n(dp371\\nVindex\\np372\\nNsVversion\\np373\\nV2.36.1\\np374\\nsVrepository_type\\np375\\nVfilesystem\\np376\\nsVlocation\\np377\\nVs:\\\\u005cpackages\\\\u005cfishbowl\\np378\\nsVname\\np379\\nVwar_foundations\\np380\\nssVkey\\np381\\nVfilesystem.variant\\np382\\nsa(dp383\\nVvariables\\np384\\n(dp385\\nVindex\\np386\\nNsVversion\\np387\\nV1.4.1\\np388\\nsVrepository_type\\np389\\nVfilesystem\\np390\\nsVlocation\\np391\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np392\\nsVname\\np393\\nVwar_menu\\np394\\nssVkey\\np395\\nVfilesystem.variant\\np396\\nsa(dp397\\nVvariables\\np398\\n(dp399\\nVindex\\np400\\nNsVversion\\np401\\nV2.4.0\\np402\\nsVrepository_type\\np403\\nVfilesystem\\np404\\nsVlocation\\np405\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np406\\nsVname\\np407\\nVwar_assets\\np408\\nssVkey\\np409\\nVfilesystem.variant\\np410\\nsa(dp411\\nVvariables\\np412\\n(dp413\\nVindex\\np414\\nNsVversion\\np415\\nV1.3.3\\np416\\nsVrepository_type\\np417\\nVfilesystem\\np418\\nsVlocation\\np419\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np420\\nsVname\\np421\\nVwar_unreal\\np422\\nssVkey\\np423\\nVfilesystem.variant\\np424\\nsa(dp425\\nVvariables\\np426\\n(dp427\\nVindex\\np428\\nNsVversion\\np429\\nV4.4.0\\np430\\nsVrepository_type\\np431\\nVfilesystem\\np432\\nsVlocation\\np433\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np434\\nsVname\\np435\\nVwar_scene\\np436\\nssVkey\\np437\\nVfilesystem.variant\\np438\\nsa(dp439\\nVvariables\\np440\\n(dp441\\nVindex\\np442\\nNsVversion\\np443\\nV1.0.5\\np444\\nsVrepository_type\\np445\\nVfilesystem\\np446\\nsVlocation\\np447\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np448\\nsVname\\np449\\nVwar_machine\\np450\\nssVkey\\np451\\nVfilesystem.variant\\np452\\nsa(dp453\\nVvariables\\np454\\n(dp455\\nVindex\\np456\\nNsVversion\\np457\\nV1.0.6\\np458\\nsVrepository_type\\np459\\nVfilesystem\\np460\\nsVlocation\\np461\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np462\\nsVname\\np463\\nVwar_anim\\np464\\nssVkey\\np465\\nVfilesystem.variant\\np466\\nsa(dp467\\nVvariables\\np468\\n(dp469\\nVindex\\np470\\nNsVversion\\np471\\nV0.3.0\\np472\\nsVrepository_type\\np473\\nVfilesystem\\np474\\nsVlocation\\np475\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np476\\nsVname\\np477\\nVwar_compass\\np478\\nssVkey\\np479\\nVfilesystem.variant\\np480\\nsa(dp481\\nVvariables\\np482\\n(dp483\\nVindex\\np484\\nI1\\nsVversion\\np485\\nV2.1.1\\np486\\nsVrepository_type\\np487\\nVfilesystem\\np488\\nsVlocation\\np489\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np490\\nsVname\\np491\\nVwar_maya_blendshapeRecv\\np492\\nssVkey\\np493\\nVfilesystem.variant\\np494\\nsa(dp495\\nVvariables\\np496\\n(dp497\\nVindex\\np498\\nNsVversion\\np499\\nV1.0.0\\np500\\nsVrepository_type\\np501\\nVfilesystem\\np502\\nsVlocation\\np503\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np504\\nsVname\\np505\\nVwar_maya\\np506\\nssVkey\\np507\\nVfilesystem.variant\\np508\\nsa(dp509\\nVvariables\\np510\\n(dp511\\nVindex\\np512\\nNsVversion\\np513\\nV1.7.1\\np514\\nsVrepository_type\\np515\\nVfilesystem\\np516\\nsVlocation\\np517\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np518\\nsVname\\np519\\nVwar_maya_common\\np520\\nssVkey\\np521\\nVfilesystem.variant\\np522\\nsa(dp523\\nVvariables\\np524\\n(dp525\\nVindex\\np526\\nNsVversion\\np527\\nV0.14\\np528\\nsVrepository_type\\np529\\nVfilesystem\\np530\\nsVlocation\\np531\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np532\\nsVname\\np533\\nVdocutils\\np534\\nssVkey\\np535\\nVfilesystem.variant\\np536\\nsa(dp537\\nVvariables\\np538\\n(dp539\\nVindex\\np540\\nI0\\nsVversion\\np541\\nV4.04.1\\np542\\nsVrepository_type\\np543\\nVfilesystem\\np544\\nsVlocation\\np545\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np546\\nsVname\\np547\\nVwmPolyGoodies\\np548\\nssVkey\\np549\\nVfilesystem.variant\\np550\\nsa(dp551\\nVvariables\\np552\\n(dp553\\nVindex\\np554\\nNsVversion\\np555\\nV4.6.1\\np556\\nsVrepository_type\\np557\\nVfilesystem\\np558\\nsVlocation\\np559\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np560\\nsVname\\np561\\nVwar_maya_validation\\np562\\nssVkey\\np563\\nVfilesystem.variant\\np564\\nsa(dp565\\nVvariables\\np566\\n(dp567\\nVindex\\np568\\nNsVversion\\np569\\nV2.5.1\\np570\\nsVrepository_type\\np571\\nVfilesystem\\np572\\nsVlocation\\np573\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np574\\nsVname\\np575\\nVwar_ocio\\np576\\nssVkey\\np577\\nVfilesystem.variant\\np578\\nsa(dp579\\nVvariables\\np580\\n(dp581\\nVindex\\np582\\nI0\\nsVversion\\np583\\nV7.3.1\\np584\\nsVrepository_type\\np585\\nVfilesystem\\np586\\nsVlocation\\np587\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cthirdparty\\np588\\nsVname\\np589\\nVrv\\np590\\nssVkey\\np591\\nVfilesystem.variant\\np592\\nsa(dp593\\nVvariables\\np594\\n(dp595\\nVindex\\np596\\nNsVversion\\np597\\nV4.2.0\\np598\\nsVrepository_type\\np599\\nVfilesystem\\np600\\nsVlocation\\np601\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np602\\nsVname\\np603\\nVwar_scene_maya\\np604\\nssVkey\\np605\\nVfilesystem.variant\\np606\\nsa(dp607\\nVvariables\\np608\\n(dp609\\nVindex\\np610\\nI0\\nsVversion\\np611\\nV1.8.1\\np612\\nsVrepository_type\\np613\\nVfilesystem\\np614\\nsVlocation\\np615\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np616\\nsVname\\np617\\nVwmModels\\np618\\nssVkey\\np619\\nVfilesystem.variant\\np620\\nsa(dp621\\nVvariables\\np622\\n(dp623\\nVindex\\np624\\nI0\\nsVversion\\np625\\nV6.17.1\\np626\\nsVrepository_type\\np627\\nVfilesystem\\np628\\nsVlocation\\np629\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np630\\nsVname\\np631\\nVwmMisc\\np632\\nssVkey\\np633\\nVfilesystem.variant\\np634\\nsa(dp635\\nVvariables\\np636\\n(dp637\\nVindex\\np638\\nI0\\nsVversion\\np639\\nV2.6.1\\np640\\nsVrepository_type\\np641\\nVfilesystem\\np642\\nsVlocation\\np643\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np644\\nsVname\\np645\\nVwmVertCopy\\np646\\nssVkey\\np647\\nVfilesystem.variant\\np648\\nsa(dp649\\nVvariables\\np650\\n(dp651\\nVindex\\np652\\nI0\\nsVversion\\np653\\nV0.33.11\\np654\\nsVrepository_type\\np655\\nVfilesystem\\np656\\nsVlocation\\np657\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np658\\nsVname\\np659\\nVAsfAmc\\np660\\nssVkey\\np661\\nVfilesystem.variant\\np662\\nsa(dp663\\nVvariables\\np664\\n(dp665\\nVindex\\np666\\nI0\\nsVversion\\np667\\nV1.51.2\\np668\\nsVrepository_type\\np669\\nVfilesystem\\np670\\nsVlocation\\np671\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np672\\nsVname\\np673\\nVwmAnim\\np674\\nssVkey\\np675\\nVfilesystem.variant\\np676\\nsa(dp677\\nVvariables\\np678\\n(dp679\\nVindex\\np680\\nNsVversion\\np681\\nV1.2.1\\np682\\nsVrepository_type\\np683\\nVfilesystem\\np684\\nsVlocation\\np685\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cfishbowl\\np686\\nsVname\\np687\\nVweta_cre\\np688\\nssVkey\\np689\\nVfilesystem.variant\\np690\\nsa(dp691\\nVvariables\\np692\\n(dp693\\nVindex\\np694\\nNsVversion\\np695\\nV0.2.0\\np696\\nsVrepository_type\\np697\\nVfilesystem\\np698\\nsVlocation\\np699\\nVc:\\\\u005cstore\\\\u005cpackages\\\\u005cweta\\np700\\nsVname\\np701\\nVweta_maya_models\\np702\\nssVkey\\np703\\nVfilesystem.variant\\np704\\nsasVnum_loaded_packages\\np705\\nI194\\nsVsolve_time\\np706\\nF2.2200000286102295\\nsVimplicit_packages\\np707\\n(lp708\\nV~platform==windows\\np709\\naV~arch==AMD64\\np710\\naV~os==windows-10.0.18362\\np711\\nasVparent_suite_path\\np712\\nNsVgraph\\np713\\nV{'nodes': [((('fillcolor', '#AAFFAA'), ('fontsize', 10), ('style', 'filled')), [('_62', 'wmModels-1.8.1[0]'), ('_63', 'wmMisc-6.17.1[0]'), ('_60', 'rv-7.3.1[0]'), ('_61', 'war_scene_maya-4.2.0[]'), ('_66', 'wmAnim-1.51.2[0]'), ('_67', 'weta_cre-1.2.1[]'), ('_64', 'wmVertCopy-2.6.1[0]'), ('_65', 'AsfAmc-0.33.11[0]'), ('_68', 'weta_maya_models-0.2.0[]'), ('_19', 'maya_common_fishbowl-0.1.0[]'), ('_39', 'war-1.0.0[]'), ('_38', 'shotgun_api3-3.0.40[]'), ('_31', 'python-2.7.14[]'), ('_30', 'anytree-2.2.2[]'), ('_33', 'functools32-3.2.3.post2[]'), ('_32', 'p4python-2017.2.1615960[0]'), ('_35', 'rez_api-2.47.2[0]'), ('_34', 'jsonschema-2.6.0[0]'), ('_37', 'war_qt-1.4.0[]'), ('_36', 'qt_py-1.2.2[]'), ('_59', 'war_ocio-2.5.1[]'), ('_58', 'war_maya_validation-4.6.1[]'), ('_53', 'war_maya_blendshapeRecv-2.1.1[1]'), ('_52', 'war_compass-0.3.0[]'), ('_51', 'war_anim-1.0.6[]'), ('_50', 'war_machine-1.0.5[]'), ('_57', 'wmPolyGoodies-4.04.1[0]'), ('_56', 'docutils-0.14[]'), ('_55', 'war_maya_common-1.7.1[]'), ('_54', 'war_maya-1.0.0[]'), ('_28', 'vray_for_maya-4.12.1.1[0]'), ('_29', 'six-1.10.0[]'), ('_26', 'mtoa-2019.2.0[0]'), ('_27', 'chaosgroup_license-1.0.0[]'), ('_24', 'maya_live_link-2.0[3]'), ('_25', 'mgear-3.1.1[0]'), ('_22', 'autodesk_license-1.0.0[]'), ('_23', 'maya-2019.2.0[0]'), ('_20', 'platform-windows[]'), ('_21', 'arch-AMD64[]'), ('_48', 'war_unreal-1.3.3[]'), ('_49', 'war_scene-4.4.0[]'), ('_40', 'ffmpeg-4.0.2[0]'), ('_41', 'enum34-1.1.6[]'), ('_42', 'future-0.16.0[0]'), ('_43', 'ffmpeg_python-0.2.0[]'), ('_44', 'requests-2.14.2[]'), ('_45', 'war_foundations-2.36.1[]'), ('_46', 'war_menu-1.4.1[]'), ('_47', 'war_assets-2.4.0[]')]), ((('fillcolor', '#F6F6F6'), ('fontsize', 10), ('style', 'filled,dashed')), [('_99', 'war_maya_common-1'), ('_98', 'docutils-0.14'), ('_97', 'war_maya-1'), ('_96', 'war_scene-4'), ('_95', 'war_machine-1'), ('_94', 'war_unreal-1'), ('_93', 'war_assets-2'), ('_92', 'war_foundations'), ('_91', 'enum34'), ('_90', 'war_qt-1'), ('_69', 'autodesk_license-1.0.0'), ('_88', 'anytree-2.2.2'), ('_89', 'war_foundations-2'), ('_84', 'requests-2.14.2'), ('_85', 'rez_api-2.47.2'), ('_86', 'war-1'), ('_87', 'shotgun_api3'), ('_80', 'enum34-1.1.6'), ('_81', 'ffmpeg_python-0.2.0'), ('_82', 'jsonschema-2.6.0'), ('_83', 'p4python-2017.2.1615960'), ('_108', 'wmVertCopy-2.6.1'), ('_107', 'wmModels-1.8.1'), ('_102', 'shotgun_api3-3.0.40'), ('_103', 'war_assets-2.1+'), ('_104', 'AsfAmc-0.33.11'), ('_105', 'wmAnim-1.51.2'), ('_106', 'wmMisc-6.17.1'), ('_79', 'future-0.16.0'), ('_78', 'ffmpeg-4.0.2'), ('_75', 'python-2.7'), ('_74', 'six-1.10.0'), ('_77', 'qt_py-1.2.2'), ('_76', 'functools32-3.2.3.post2'), ('_71', 'arch-AMD64'), ('_70', 'platform-windows'), ('_73', 'chaosgroup_license-1.0.0'), ('_72', 'maya-2019'), ('_100', 'wmPolyGoodies-4.04'), ('_101', 'rv-7.3.1')]), ((('fillcolor', '#FFFFAA'), ('fontsize', 10), ('style', 'filled,dashed')), [('_9', 'war_maya_blendshapeRecv-2'), ('_8', 'war_compass-0.3.0'), ('_7', 'war_anim-1.0.6'), ('_6', 'vray_for_maya-4.12.1.1'), ('_5', 'mtoa-2019.2.0'), ('_4', 'mgear-3.1.1'), ('_3', 'maya-2019.2.0'), ('_2', 'maya_live_link-2.0'), ('_1', 'maya_common_fishbowl-0.1.0'), ('_17', '~arch==AMD64'), ('_16', '~platform==windows'), ('_15', 'weta_maya_models-0.2.0'), ('_14', 'weta_cre-1.2.1'), ('_13', 'war_scene_maya-4'), ('_12', 'war_ocio-2'), ('_11', 'war_menu-1'), ('_10', 'war_maya_validation-4'), ('_18', '~os==windows-10.0.18362')])], 'edges': [((('arrowsize', '0.5'),), [('_99', '_55'), ('_98', '_56'), ('_97', '_54'), ('_96', '_49'), ('_95', '_50'), ('_94', '_48'), ('_93', '_47'), ('_92', '_45'), ('_91', '_41'), ('_90', '_37'), ('_62', '_70'), ('_62', '_71'), ('_62', '_72'), ('_63', '_70'), ('_63', '_71'), ('_63', '_72'), ('_60', '_70'), ('_60', '_71'), ('_61', '_80'), ('_61', '_77'), ('_61', '_101'), ('_61', '_102'), ('_61', '_103'), ('_61', '_99'), ('_61', '_96'), ('_61', '_11'), ('_61', '_94'), ('_66', '_70'), ('_66', '_71'), ('_66', '_72'), ('_67', '_104'), ('_67', '_105'), ('_67', '_106'), ('_67', '_107'), ('_67', '_108'), ('_64', '_70'), ('_64', '_71'), ('_64', '_72'), ('_65', '_70'), ('_65', '_71'), ('_65', '_72'), ('_68', '_11'), ('_69', '_22'), ('_88', '_30'), ('_89', '_45'), ('_84', '_44'), ('_85', '_35'), ('_86', '_39'), ('_87', '_38'), ('_80', '_41'), ('_81', '_43'), ('_82', '_34'), ('_83', '_32'), ('_108', '_64'), ('_9', '_53'), ('_8', '_52'), ('_7', '_51'), ('_6', '_28'), ('_5', '_26'), ('_4', '_25'), ('_3', '_23'), ('_2', '_24'), ('_1', '_19'), ('_107', '_62'), ('_17', '_21'), ('_16', '_20'), ('_15', '_68'), ('_14', '_67'), ('_13', '_61'), ('_12', '_59'), ('_11', '_46'), ('_10', '_58'), ('_102', '_38'), ('_103', '_47'), ('_104', '_65'), ('_105', '_66'), ('_106', '_63'), ('_30', '_74'), ('_32', '_70'), ('_32', '_71'), ('_32', '_75'), ('_35', '_70'), ('_35', '_71'), ('_35', '_75'), ('_34', '_76'), ('_34', '_70'), ('_34', '_71'), ('_34', '_75'), ('_37', '_77'), ('_58', '_98'), ('_58', '_89'), ('_58', '_99'), ('_58', '_11'), ('_58', '_90'), ('_58', '_100'), ('_53', '_70'), ('_53', '_71'), ('_53', '_72'), ('_52', '_89'), ('_51', '_89'), ('_51', '_95'), ('_51', '_96'), ('_51', '_11'), ('_50', '_89'), ('_57', '_70'), ('_57', '_71'), ('_57', '_72'), ('_55', '_74'), ('_55', '_89'), ('_55', '_97'), ('_28', '_73'), ('_28', '_70'), ('_28', '_71'), ('_28', '_72'), ('_26', '_3'), ('_26', '_70'), ('_26', '_71'), ('_24', '_70'), ('_24', '_71'), ('_24', '_72'), ('_25', '_70'), ('_25', '_71'), ('_23', '_69'), ('_23', '_70'), ('_23', '_71'), ('_48', '_92'), ('_49', '_80'), ('_49', '_93'), ('_49', '_89'), ('_49', '_94'), ('_40', '_70'), ('_40', '_71'), ('_42', '_70'), ('_42', '_71'), ('_42', '_75'), ('_43', '_78'), ('_43', '_79'), ('_43', '_74'), ('_45', '_80'), ('_45', '_81'), ('_45', '_82'), ('_45', '_83'), ('_45', '_84'), ('_45', '_85'), ('_45', '_74'), ('_45', '_86'), ('_45', '_87'), ('_46', '_88'), ('_46', '_74'), ('_46', '_89'), ('_46', '_90'), ('_47', '_74'), ('_47', '_91'), ('_79', '_42'), ('_78', '_40'), ('_75', '_31'), ('_74', '_29'), ('_77', '_36'), ('_76', '_33'), ('_71', '_21'), ('_70', '_20'), ('_73', '_27'), ('_72', '_23'), ('_100', '_57'), ('_101', '_60')])]}\\np714\\nsVpackage_paths\\np715\\n(lp716\\nVC:\\\\u005cUsers\\\\u005cnathan\\\\u005cPackages\\np717\\naVC:\\\\u005cUsers\\\\u005cnathan\\\\u005cUserPackages\\np718\\naVY:\\\\u005c\\np719\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cFishbowl\\np720\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cPerforce\\np721\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cProjects\\np722\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cThirdParty\\np723\\naVC:\\\\u005cstore\\\\u005cPackages\\\\u005cWeta\\np724\\naVS:\\\\u005cPackages\\\\u005cFishbowl\\np725\\naVS:\\\\u005cPackages\\\\u005cPerforce\\np726\\naVS:\\\\u005cPackages\\\\u005cProjects\\np727\\naVS:\\\\u005cPackages\\\\u005cThirdParty\\np728\\naVS:\\\\u005cPackages\\\\u005cWeta\\np729\\nasVplatform\\np730\\nVwindows\\np731\\nsVrez_path\\np732\\nVc:\\\\u005cprogra~1\\\\u005crez\\\\u005clib\\\\u005csite-packages\\\\u005crez\\np733\\nsVpatch_locks\\np734\\n(dp735\\nsVdefault_patch_lock\\np736\\nVno_lock\\np737\\nsVsuite_context_name\\np738\\nNsVserialize_version\\np739\\nV4.3\\np740\\nsVtimestamp\\np741\\nI1587509795\\nsVhost\\np742\\nVSNAPE\\np743\\nsVuser\\np744\\nVnathan\\np745\\nsVload_time\\np746\\nF0.0\\nsVpackage_filter\\np747\\n(lp748\\nsVarch\\np749\\nVAMD64\\np750\\nsVbuilding\\np751\\nI00\\nsVrequested_timestamp\\np752\\nNsVpackage_orderers\\np753\\nNsVpackage_requests\\np754\\n(lp755\\nVmaya_common_fishbowl-0.1.0\\np756\\naVmaya_live_link-2.0\\np757\\naVmaya-2019.2.0\\np758\\naVmgear-3.1.1\\np759\\naVmtoa-2019.2.0\\np760\\naVvray_for_maya-4.12.1.1\\np761\\naVwar_anim-1.0.6\\np762\\naVwar_compass-0.3.0\\np763\\naVwar_maya_blendshapeRecv-2\\np764\\naVwar_maya_validation-4\\np765\\naVwar_menu-1\\np766\\naVwar_ocio-2\\np767\\naVwar_scene_maya-4\\np768\\naVweta_cre-1.2.1\\np769\\naVweta_maya_models-0.2.0\\np770\\nasVfailure_description\\np771\\nNsVcreated\\np772\\nI1587509795\\nsVstatus\\np773\\nVsolved\\np774\\nsVfrom_cache\\np775\\nI00\\nsVcaching\\np776\\nI01\\nsVos\\np777\\nVwindows-10.0.18362\\np778\\ns.\"\nendStream\nendChannel\nendAssociations\n" 
		-scn;
// End of global_control_prp.ma
