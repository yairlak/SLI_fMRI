clear all; close all; clc
%%
stim_order.run1.ZM = [1:8, 12:16, 34, 37, 40];
stim_order.run2.ZM = [9 11 17:19 21 22 23 24 26 27 28 29 30 32 40];
stim_order.run3.ZM = [1 3 4 7 10 20 22 24 25 28 31 33 35 36 38 39];

stim_order.run1.SZVO = [10:11, 20:25];
stim_order.run2.SZVO = [1:5 7 8 33];
stim_order.run3.SZVO = [6 12:14 18:19 29 37];

stim_order.run1.SVOZ = [9, 17, 19, 28:30, 36, 39];
stim_order.run2.SVOZ = [13:16 20 31 35 38];
stim_order.run3.SVOZ = [8 21 23 26 27 32 34 40]; 

stim_order.run1.OVS = [18 27 31 32 33];
stim_order.run2.OVS = [6 10 12 25];
stim_order.run3.OVS = [9 16 30];

stim_order.run1.MIDDLE = [38 35 26 33];
stim_order.run2.MIDDLE = [34 36 37 39];
stim_order.run3.MIDDLE = [2 5 11 15];

ALL1 = [stim_order.run1.ZM, stim_order.run1.SZVO, stim_order.run1.SVOZ, stim_order.run1.OVS, stim_order.run1.MIDDLE];
ALL2 = [stim_order.run2.ZM, stim_order.run2.SZVO, stim_order.run2.SVOZ, stim_order.run2.OVS, stim_order.run2.MIDDLE];
ALL3 = [stim_order.run3.ZM, stim_order.run3.SZVO, stim_order.run3.SVOZ, stim_order.run3.OVS, stim_order.run3.MIDDLE];

ALL1 = sort(ALL1);
ALL2 = sort(ALL2);
ALL3 = sort(ALL3);

length(ALL1) == length(union(ALL1, ALL1))
length(ALL2) == length(union(ALL2, ALL2))
length(ALL3) == length(union(ALL3, ALL3))
%%
gen_figs = false;
if gen_figs
    mat1(1, stim_order.run1.ZM) = 1;
    mat1(2, stim_order.run1.SZVO)= 1;
    mat1(3, stim_order.run1.SVOZ)= 1;
    mat1(4, stim_order.run1.OVS)= 1;
    mat1(5, stim_order.run1.MIDDLE)= 1;

    mat2(1, stim_order.run2.ZM) = 1;
    mat2(2, stim_order.run2.SZVO)= 1;
    mat2(3, stim_order.run2.SVOZ)= 1;
    mat2(4, stim_order.run2.OVS)= 1;
    mat2(5, stim_order.run2.MIDDLE)= 1;

    mat3(1, stim_order.run3.ZM) = 1;
    mat3(2, stim_order.run3.SZVO)= 1;
    mat3(3, stim_order.run3.SVOZ)= 1;
    mat3(4, stim_order.run3.OVS)= 1;
    mat3(5, stim_order.run3.MIDDLE)= 1;

    figure('color', [1 1 1])
    imagesc(mat1);

    figure('color', [1 1 1])
    imagesc(mat2);

    figure('color', [1 1 1])
    imagesc(mat3);

    figure('color', [1 1 1])
    imagesc([mat1(1, :); mat2(1, :); mat3(1, :)]);

    figure('color', [1 1 1])
    imagesc([mat1(2, :); mat2(2, :); mat3(2, :)]);

    figure('color', [1 1 1])
    imagesc([mat1(3, :); mat2(3, :); mat3(3, :)]);

    figure('color', [1 1 1])
    imagesc([mat1(4, :); mat2(4, :); mat3(4, :)]);

    figure('color', [1 1 1])
    imagesc([mat1(5, :); mat2(5, :); mat3(5, :)]);
end