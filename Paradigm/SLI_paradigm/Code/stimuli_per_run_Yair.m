clear all; close all; clc

%%
OVS = [6,9,10,12,16,18,25,27,30,31,32,33];
MIDDLE = [2,5,11,15,17,26,34:39];
SVOZ = [8,9,13:17,19:21,23,26:32,34:36,38:40];
SZVO = [1:8,10:14,18:25,29,33,37];

%%
OVS_1 = OVS([1 6 3 4]); 
OVS_2 = OVS([5 2 7 8]);
OVS_3 = OVS([9 10 11 12]);
MIDDLE_1 = MIDDLE([7 2 3 8]); 
MIDDLE_2 = MIDDLE([5 6 1 4]);
MIDDLE_3 = MIDDLE([9 10 11 12]);
FILLER_1 = union(OVS_1, MIDDLE_1);
FILLER_2 = union(OVS_2, MIDDLE_2);
FILLER_3 = union(OVS_3, MIDDLE_3);
SVOZ_1 = [19 20 21 27 28 30 31:32];
SVOZ_2 = [23 29 34:36 38:40];
SVOZ_3 = [8 13 14 9 15:16 17 26];
SZVO_1 = [8 13 14 22 24 25 33 37];
SZVO_2 = [19 20 21 7 10 11 12 18];
SZVO_3 = [23 29 1:6];

SVO_1 = union(SVOZ_1, SZVO_1);
SVO_2 = union(SVOZ_2, SZVO_2);
SVO_3 = union(SVOZ_3, SZVO_3);

SVO_FILLER_1 = union(SVO_1, FILLER_1);
SVO_FILLER_2 = union(SVO_2, FILLER_2);
SVO_FILLER_3 = union(SVO_3, FILLER_3);

ZM_1 = setdiff(1:40, SVO_FILLER_1);
ZM_2 = setdiff(1:40, SVO_FILLER_2);
ZM_3 = setdiff(1:40, SVO_FILLER_3);

stim_numbers.run1.ZM = ZM_1;
stim_numbers.run1.SVOZ = SVOZ_1;
stim_numbers.run1.SZVO = SZVO_1;
stim_numbers.run1.OVS = OVS_1;
stim_numbers.run1.MIDDLE = MIDDLE_1;

stim_numbers.run2.ZM = ZM_2;
stim_numbers.run2.SVOZ = SVOZ_2;
stim_numbers.run2.SZVO = SZVO_2;
stim_numbers.run2.OVS = OVS_2;
stim_numbers.run2.MIDDLE = MIDDLE_2;

stim_numbers.run3.ZM = ZM_3;
stim_numbers.run3.SVOZ = SVOZ_3;
stim_numbers.run3.SZVO = SZVO_3;
stim_numbers.run3.OVS = OVS_3;
stim_numbers.run3.MIDDLE = MIDDLE_3;

save('stim_order_per_run.mat', 'stim_numbers');
mat(SVOZ_1, 1) = 1;
mat(SZVO_1, 2) = 1;
mat(ZM_1, 3) = 1;
mat(FILLER_1, 4) = 1;
mat(SVOZ_2, 5) = 2;
mat(SZVO_2, 6) = 2;
mat(ZM_2, 7) = 2;
mat(FILLER_2, 8) = 2;
mat(SVOZ_3, 9) = 3;
mat(SZVO_3, 10) = 3;
mat(ZM_3, 11) = 3;
mat(FILLER_3, 12) = 3;
figure('color', [1 1 1])
imagesc(mat)

ALL1 = [SVOZ_1, SZVO_1, ZM_1, FILLER_1];
ALL2 = [SVOZ_2, SZVO_2, ZM_2, FILLER_2];
ALL3 = [SVOZ_3, SZVO_3, ZM_3, FILLER_3];

intersect(SVOZ_1, SVOZ_2)
intersect(SVOZ_1, SVOZ_3)
intersect(SVOZ_2, SVOZ_3)
intersect(SZVO_1, SZVO_2)
intersect(SZVO_1, SZVO_3)
intersect(SZVO_2, SZVO_3)
intersect(FILLER_1, FILLER_2)
intersect(FILLER_2, FILLER_3)
intersect(FILLER_1, FILLER_3)
intersect(SVO_1, FILLER_1)
intersect(SVO_2, FILLER_2)
intersect(SVO_3, FILLER_3)
intersect(ZM_1, SVO_1)
intersect(ZM_1, ZM_2)
intersect(ZM_2, ZM_3)
intersect(ZM_1, ZM_3)

length(ALL1) == length(union(ALL1, ALL1))
length(ALL2) == length(union(ALL2, ALL2))
length(ALL3) == length(union(ALL3, ALL3))

% curr_mid = MIDDLE;
% curr_ovs = OVS;
% ZM_comp1 = SVO_1;
% cnt = 1;
% while length(ZM_comp1)<=24;
%     if ~ismember(curr_mid(cnt), SVO_1)
%         ZM_comp1 = [ZM_comp1 curr_mid(cnt)];
%         curr_mid(cnt) = [];
%     end
%     cnt = cnt + 1;
% end