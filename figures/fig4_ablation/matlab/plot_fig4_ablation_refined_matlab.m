function outputs = plot_fig4_ablation_refined_matlab()
%PLOT_FIG4_ABLATION_REFINED_MATLAB Reproduce the audited refined Fig. 4.
%
% MATLAB R2021a compatible. This file is visualization-only: it does not
% train, infer, tune, split, aggregate, or modify any experiment data.
%
% Authoritative sources (read-only, in the parent directory):
%   AUTHORITATIVE_A1_A6.csv
%   ABLATION_RECOMPUTED.csv
%   A1_A6_lifecycle_variation.csv
%   A1_A6_cumulative_variation.csv

close all force;

scriptDir = fileparts(mfilename('fullpath'));
dataDir = fileparts(scriptDir);

summaryPath = fullfile(dataDir, 'AUTHORITATIVE_A1_A6.csv');
auditPath = fullfile(dataDir, 'ABLATION_RECOMPUTED.csv');
localPath = fullfile(dataDir, 'A1_A6_lifecycle_variation.csv');
cumulativePath = fullfile(dataDir, 'A1_A6_cumulative_variation.csv');

[summary, localVariation, cumulativeVariation] = loadAndValidateData( ...
    summaryPath, auditPath, localPath, cumulativePath);

S = figureStyle();
fig = figure( ...
    'Color', 'w', ...
    'Units', 'inches', ...
    'Position', [0.25 0.25 7.2 5.75], ...
    'PaperUnits', 'inches', ...
    'PaperSize', [7.2 5.75], ...
    'PaperPosition', [0 0 7.2 5.75], ...
    'PaperPositionMode', 'manual', ...
    'Renderer', 'painters', ...
    'InvertHardcopy', 'off');

% Fixed normalized geometry mirrors the accepted Python figure.
panelPos = [ ...
    0.0850 0.6370 0.3544 0.3410; ... % (a)
    0.5705 0.6370 0.3544 0.3410; ... % (b)
    0.0850 0.1050 0.3544 0.3410; ... % (c)
    0.5705 0.1050 0.3544 0.3410];    % (d)

axA = axes(fig, 'Position', panelPos(1, :));
drawPanelA(axA, summary, S);

axB = axes(fig, 'Position', panelPos(2, :));
drawPanelB(axB, localVariation, S);

axC = axes(fig, 'Position', panelPos(3, :));
drawPanelC(axC, summary, S);

axD = axes(fig, 'Position', panelPos(4, :));
drawPanelD(axD, cumulativeVariation, S);

drawnow;

outputs.pdf = fullfile(scriptDir, 'fig4_ablation_refined_matlab.pdf');
outputs.png = fullfile(scriptDir, 'fig4_ablation_refined_matlab.png');
outputs.svg = fullfile(scriptDir, 'fig4_ablation_refined_matlab.svg');
outputs.fig = fullfile(scriptDir, 'fig4_ablation_refined_matlab.fig');

print(fig, outputs.pdf, '-dpdf', '-painters');
print(fig, outputs.png, '-dpng', '-r600');
print(fig, outputs.svg, '-dsvg', '-painters');
savefig(fig, outputs.fig, 'compact');

fprintf('[Fig4 MATLAB] protocol changed: False\n');
fprintf('[Fig4 MATLAB] training performed: False\n');
fprintf('[Fig4 MATLAB] rows validated: local=%d, cumulative=%d\n', ...
    height(localVariation), height(cumulativeVariation));
fprintf('[Fig4 MATLAB output] %s\n', outputs.pdf);
fprintf('[Fig4 MATLAB output] %s\n', outputs.png);
fprintf('[Fig4 MATLAB output] %s\n', outputs.svg);
fprintf('[Fig4 MATLAB output] %s\n', outputs.fig);
end


function [summary, localVariation, cumulativeVariation] = loadAndValidateData( ...
    summaryPath, auditPath, localPath, cumulativePath)

summary = readtable(summaryPath, 'VariableNamingRule', 'preserve');
audit = readtable(auditPath, 'VariableNamingRule', 'preserve');
localVariation = readtable(localPath, 'VariableNamingRule', 'preserve');
cumulativeVariation = readtable(cumulativePath, 'VariableNamingRule', 'preserve');

methods = ["A1"; "A2"; "A3"; "A4"; "A5"; "A6"];
assert(height(summary) == 6, 'Authoritative summary must contain six rows.');
assert(isequal(string(summary{:, 1}), methods), 'Authoritative summary is not ordered A1-A6.');
assert(height(localVariation) == 1824, 'Local variation table must contain 1824 rows.');
assert(height(cumulativeVariation) == 1824, 'Cumulative variation table must contain 1824 rows.');

localIDs = string(localVariation{:, 1});
cumulativeIDs = string(cumulativeVariation{:, 1});
for i = 1:numel(methods)
    assert(sum(localIDs == methods(i)) == 304, '%s local table does not have 304 rows.', methods(i));
    assert(sum(cumulativeIDs == methods(i)) == 304, '%s cumulative table does not have 304 rows.', methods(i));
end

% Complete M-Precision only from the already audited recomputation table.
auditIDs = string(audit{:, 1});
auditMetric = string(audit{:, 2});
isMPrecision = auditMetric == "M-Precision";
assert(sum(isMPrecision) == 6, 'Expected six audited M-Precision rows.');
assert(max(abs(audit{isMPrecision, 5})) <= 1e-12, 'M-Precision audit differences are non-zero.');

mPrecision = nan(6, 1);
for i = 1:numel(methods)
    row = isMPrecision & auditIDs == methods(i);
    assert(sum(row) == 1, 'Missing audited M-Precision for %s.', methods(i));
    mPrecision(i) = audit{row, 4};
end
summary.M_Precision_Audited = mPrecision;

% Hard consistency checks: local mean and cumulative endpoint reproduce Smooth.
smooth = summary{:, 11};
for i = 1:numel(methods)
    localRows = localIDs == methods(i);
    cumulativeRows = cumulativeIDs == methods(i);
    localBlock = sortrows(localVariation(localRows, :), 'run_id');
    cumulativeBlock = sortrows(cumulativeVariation(cumulativeRows, :), 'run_id');
    localMean = mean(localBlock.local_variation_l1, 'omitnan');
    endpoint = cumulativeBlock.cumulative_variation_l1(end);
    assert(abs(localMean - smooth(i)) <= 5e-10, '%s local mean does not reproduce Smooth.', methods(i));
    assert(abs(endpoint / 303 - smooth(i)) <= 5e-10, '%s cumulative endpoint does not reproduce Smooth.', methods(i));
end
end


function S = figureStyle()
S.font = 'Arial';
S.fontSize = 7.0;
S.axisLabelSize = 7.15;
S.tickSize = 6.45;
S.legendSize = 5.75;
S.annotationSize = 5.2;
S.valueSize = 4.55;
S.titleSize = 7.35;
S.axisWidth = 0.72;

S.navy = hex2rgb('#193B5A');
S.blue = hex2rgb('#2F6688');
S.teal = hex2rgb('#287F8A');
S.cyan = hex2rgb('#69B7C1');
S.gold = hex2rgb('#D99227');
S.rust = hex2rgb('#B65A3A');
S.slate = hex2rgb('#697783');
S.grey = hex2rgb('#AEB7BE');
S.text = hex2rgb('#252B2F');
S.grid = hex2rgb('#E4E8EB');
S.a5bg = blendWithWhite(hex2rgb('#FBF0DD'), 0.58);
S.a6bg = blendWithWhite(hex2rgb('#E5F2F3'), 0.58);

S.methodColors = [ ...
    hex2rgb('#8B949C'); ...
    hex2rgb('#8AA9BA'); ...
    hex2rgb('#5F89A5'); ...
    hex2rgb('#315E7D'); ...
    hex2rgb('#D6922E'); ...
    hex2rgb('#0B6174')];
S.methodMarkers = {'o', 's', '^', 'd', '+', 'x'};
end


function drawPanelA(ax, summary, S)
methods = {'A1', 'A2', 'A3', 'A4', 'A5', 'A6'};
x = 1:6;
baseline = 0.96;
width = 0.215;
values = [summary{:, 3}, summary{:, 4}, summary{:, 5}];
colors = [S.navy; S.teal; S.cyan];

yyaxis(ax, 'left');
hold(ax, 'on');
drawHighlights(ax, S, 0.96, 1.002);
barHandles = gobjects(3, 1);
for j = 1:3
    xpos = x + (j - 2) * width;
    barHandles(j) = bar(ax, xpos, values(:, j), width * 0.90, ...
        'FaceColor', colors(j, :), ...
        'EdgeColor', 'w', 'LineWidth', 0.42);
    drawBarOutline(ax, xpos(5), baseline, values(5, j), width * 0.90, S.methodColors(5, :));
    drawBarOutline(ax, xpos(6), baseline, values(6, j), width * 0.90, S.methodColors(6, :));
end

xlim(ax, [0.55 6.45]);
ylim(ax, [0.96 1.002]);
yticks(ax, [0.96 0.97 0.98 0.99 1.00]);
ytickformat(ax, '%.2f');
xticks(ax, x);
xticklabels(ax, methods);
ylabel(ax, 'Score (higher is better)');
styleAxis(ax, S);

% A6 predictive-performance callout on the left axis.
text(ax, 5.10, 0.9966, 'A6: accuracy restored', ...
    'Color', S.methodColors(6, :), 'FontName', S.font, ...
    'FontSize', S.annotationSize, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'left', 'VerticalAlignment', 'top');
dataArrow(ax, 5.92, 0.9942, 5.78, values(6, 1) + 0.0003, ...
    [0.55 6.45], [0.96 1.002], S.methodColors(6, :));

yyaxis(ax, 'right');
smooth = summary{:, 11};
smoothHandle = plot(ax, x, smooth, '-o', ...
    'Color', S.gold, 'LineWidth', 1.42, 'MarkerSize', 4.0, ...
    'MarkerFaceColor', 'w', 'MarkerEdgeColor', S.gold);
ylim(ax, [0.0110 0.0257]);
yticks(ax, [0.012 0.016 0.020 0.024]);
ytickformat(ax, '%.3f');
ylabel(ax, 'Smooth (lower is better)');
ax.YAxis(2).Color = S.gold;

labelOffsets = [-0.00065 0.00075 -0.00075 0.00075 0.00075 -0.00072];
for i = 1:6
    weight = 'normal';
    sizeNow = S.valueSize;
    if i >= 5
        weight = 'bold';
        sizeNow = S.valueSize + 0.3;
    end
    text(ax, x(i), smooth(i) + labelOffsets(i), sprintf('%.4f', smooth(i)), ...
        'Color', S.gold, 'BackgroundColor', 'w', 'Margin', 0.15, ...
        'FontName', S.font, 'FontSize', sizeNow, 'FontWeight', weight, ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
end

text(ax, 4.48, 0.01215, 'A5: strongest smoothing', ...
    'Color', S.methodColors(5, :), 'FontName', S.font, ...
    'FontSize', S.annotationSize, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
dataArrow(ax, 4.72, 0.01275, 5.00, smooth(5) - 0.00005, ...
    [0.55 6.45], [0.0110 0.0257], S.methodColors(5, :));

legend(ax, [barHandles(:); smoothHandle], ...
    {'Acc', 'Macro-F1', 'M-F1', 'Smooth \downarrow'}, ...
    'Interpreter', 'tex', 'Location', 'northwest', 'Orientation', 'horizontal', ...
    'NumColumns', 4, 'Box', 'off', 'FontName', S.font, 'FontSize', S.legendSize);

belowTitle(ax, 'a', ['Overall predictive performance across A1' char(8211) 'A6'], S);
end


function drawPanelB(ax, localVariation, S)
methods = ["A1", "A2", "A3", "A4", "A5", "A6"];
hold(ax, 'on');
lineHandles = gobjects(6, 1);
allIDs = string(localVariation{:, 1});

for i = 1:6
    block = sortrows(localVariation(allIDs == methods(i), :), 'run_id');
    x = block.relative_tool_life;
    raw = block.local_variation_l1;
    smoothed = block.local_variation_l1_smoothed;
    rawColor = blendWithWhite(S.methodColors(i, :), 0.12);
    plot(ax, x, raw, '-', 'Color', rawColor, 'LineWidth', 0.45);
    lineWidth = 1.05;
    markerSize = 2.2;
    if i >= 5
        lineWidth = 1.52;
        markerSize = 2.7;
    end
    lineHandles(i) = plot(ax, x, smoothed, '-', ...
        'Color', S.methodColors(i, :), 'LineWidth', lineWidth, ...
        'Marker', S.methodMarkers{i}, 'MarkerIndices', 1:52:numel(x), ...
        'MarkerSize', markerSize, 'MarkerFaceColor', 'w', ...
        'MarkerEdgeColor', S.methodColors(i, :));
end

xlim(ax, [0 1]);
ylim(ax, [0 0.70]);
xticks(ax, 0:0.2:1);
xtickformat(ax, '%.1f');
yticks(ax, 0:0.1:0.6);
xlabel(ax, 'Relative tool life');
ylabel(ax, 'Local probability variation  \Delta_t (L1)', 'Interpreter', 'tex');
styleAxis(ax, S);

lgd = legend(ax, lineHandles, cellstr(methods), ...
    'Location', 'northeast', 'Orientation', 'vertical', 'NumColumns', 1, ...
    'Box', 'on', 'Color', 'w', 'EdgeColor', S.grid, ...
    'FontName', S.font, 'FontSize', S.legendSize);
lgd.ItemTokenSize = [13 8];
lgd.AutoUpdate = 'off';

text(ax, 0.46, 0.965, 'thin = raw   \cdot   dark = centered 11-run mean', ...
    'Units', 'normalized', 'Interpreter', 'tex', ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
    'FontName', S.font, 'FontSize', 5.05, 'Color', S.slate, ...
    'BackgroundColor', 'w', 'EdgeColor', S.grid, 'Margin', 2.0);

belowTitle(ax, 'b', 'Lifecycle-wise probability variation', S);
end


function drawPanelC(ax, summary, S)
methods = {'A1', 'A2', 'A3', 'A4', 'A5', 'A6'};
x = 1:6;
baseline = 0.94;
width = 0.28;
mPrecision = summary.M_Precision_Audited;
mRecall = summary{:, 6};

yyaxis(ax, 'left');
hold(ax, 'on');
drawHighlights(ax, S, 0.94, 1.005);
bar1x = x - width / 2;
bar2x = x + width / 2;
b1 = bar(ax, bar1x, mPrecision, width * 0.90, ...
    'FaceColor', S.teal, 'EdgeColor', 'w', 'LineWidth', 0.42);
b2 = bar(ax, bar2x, mRecall, width * 0.90, ...
    'FaceColor', S.blue, 'EdgeColor', 'w', 'LineWidth', 0.42);
drawBarOutline(ax, bar1x(5), baseline, mPrecision(5), width * 0.90, S.methodColors(5, :));
drawBarOutline(ax, bar2x(5), baseline, mRecall(5), width * 0.90, S.methodColors(5, :));
drawBarOutline(ax, bar1x(6), baseline, mPrecision(6), width * 0.90, S.methodColors(6, :));
drawBarOutline(ax, bar2x(6), baseline, mRecall(6), width * 0.90, S.methodColors(6, :));

xlim(ax, [0.55 6.45]);
ylim(ax, [0.94 1.005]);
yticks(ax, [0.94 0.96 0.98 1.00]);
ytickformat(ax, '%.2f');
xticks(ax, x);
xticklabels(ax, methods);
ylabel(ax, 'Middle-stage score (higher is better)');
styleAxis(ax, S);

text(ax, 5.00, 0.987, 'A6 restores M-Rec', ...
    'Color', S.methodColors(6, :), 'FontName', S.font, ...
    'FontSize', S.annotationSize, 'FontWeight', 'bold');
dataArrow(ax, 5.88, 0.9848, 6.14, mRecall(6) + 0.0005, ...
    [0.55 6.45], [0.94 1.005], S.methodColors(6, :));

yyaxis(ax, 'right');
mToE = summary{:, 7};
mToL = summary{:, 8};
hE = plot(ax, x, mToE, '-d', 'Color', S.rust, 'LineWidth', 1.22, ...
    'MarkerSize', 3.7, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', S.rust);
hL = plot(ax, x, mToL, '-v', 'Color', S.slate, 'LineWidth', 1.22, ...
    'MarkerSize', 3.7, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', S.slate);
ylim(ax, [-0.003 0.0455]);
yticks(ax, 0:0.01:0.04);
ytickformat(ax, '%.2f');
ylabel(ax, 'Transition error rate (lower is better)');
ax.YAxis(2).Color = S.rust;

eOffsets = [0.00165 -0.00175 0.00165 -0.00175 0.00165 -0.00175];
for i = 1:6
    weight = 'normal';
    sizeNow = S.valueSize;
    if i >= 5
        weight = 'bold';
        sizeNow = S.valueSize + 0.3;
    end
    text(ax, x(i), mToE(i) + eOffsets(i), sprintf('%.3f', mToE(i)), ...
        'Color', S.rust, 'BackgroundColor', 'w', 'Margin', 0.15, ...
        'FontName', S.font, 'FontSize', sizeNow, 'FontWeight', weight, ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    text(ax, x(i), 0.00145, sprintf('%.3f', mToL(i)), ...
        'Color', S.slate, 'BackgroundColor', 'w', 'Margin', 0.15, ...
        'FontName', S.font, 'FontSize', S.valueSize, ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
end

legend(ax, [b1 b2 hE hL], ...
    {'M-Pre', 'M-Rec', 'M\rightarrowE \downarrow', 'M\rightarrowL \downarrow'}, ...
    'Interpreter', 'tex', 'Location', 'northwest', 'Orientation', 'horizontal', ...
    'NumColumns', 4, 'Box', 'off', 'FontName', S.font, 'FontSize', S.legendSize);

belowTitle(ax, 'c', 'Middle-stage and transition consistency', S);
end


function drawPanelD(ax, cumulativeVariation, S)
methods = ["A1", "A2", "A3", "A4", "A5", "A6"];
hold(ax, 'on');
lineHandles = gobjects(6, 1);
endpoints = nan(6, 1);
allIDs = string(cumulativeVariation{:, 1});

for i = 1:6
    block = sortrows(cumulativeVariation(allIDs == methods(i), :), 'run_id');
    x = block.relative_tool_life;
    y = block.cumulative_variation_l1;
    endpoints(i) = y(end);
    lineWidth = 1.08;
    markerSize = 2.15;
    if i >= 5
        lineWidth = 1.62;
        markerSize = 2.8;
    end
    lineHandles(i) = plot(ax, x, y, '-', ...
        'Color', S.methodColors(i, :), 'LineWidth', lineWidth, ...
        'Marker', S.methodMarkers{i}, 'MarkerIndices', 1:52:numel(x), ...
        'MarkerSize', markerSize, 'MarkerFaceColor', 'w', ...
        'MarkerEdgeColor', S.methodColors(i, :));
end

xlim(ax, [0 1]);
ylim(ax, [0 7.85]);
xticks(ax, 0:0.2:1);
xtickformat(ax, '%.1f');
yticks(ax, 0:1:7);
xlabel(ax, 'Relative tool life');
ylabel(ax, 'Cumulative probability variation  C_t (L1)', 'Interpreter', 'tex');
styleAxis(ax, S);

lgd = legend(ax, lineHandles, cellstr(methods), ...
    'Location', 'northwest', 'Orientation', 'vertical', 'NumColumns', 1, ...
    'Box', 'on', 'Color', 'w', 'EdgeColor', S.grid, ...
    'FontName', S.font, 'FontSize', S.legendSize);
lgd.ItemTokenSize = [13 8];
lgd.AutoUpdate = 'off';

text(ax, 0.40, 0.965, 'terminal C_t/303 = Smooth', ...
    'Units', 'normalized', 'Interpreter', 'tex', ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
    'FontName', S.font, 'FontSize', 5.05, 'Color', S.slate, ...
    'BackgroundColor', 'w', 'EdgeColor', S.grid, 'Margin', 2.0);

text(ax, 0.985, 0.965, sprintf('A6: balanced endpoint = %.2f', endpoints(6)), ...
    'Units', 'normalized', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top', ...
    'FontName', S.font, 'FontSize', S.annotationSize, 'FontWeight', 'bold', ...
    'Color', S.methodColors(6, :), 'BackgroundColor', 'w', 'Margin', 0.5);

text(ax, 0.58, 2.85, sprintf('A5: lowest total variation (%.2f)', endpoints(5)), ...
    'FontName', S.font, 'FontSize', S.annotationSize, 'FontWeight', 'bold', ...
    'Color', S.methodColors(5, :), 'BackgroundColor', 'w', 'Margin', 0.5);
dataArrow(ax, 0.81, 3.22, 0.88, endpoints(5) - 0.05, ...
    [0 1], [0 7.85], S.methodColors(5, :));

belowTitle(ax, 'd', 'Trajectory stability diagnostics', S);
end


function styleAxis(ax, S)
set(ax, ...
    'FontName', S.font, ...
    'FontSize', S.tickSize, ...
    'LineWidth', S.axisWidth, ...
    'XColor', S.text, ...
    'YColor', S.slate, ...
    'Box', 'off', ...
    'Layer', 'top', ...
    'TickDir', 'out', ...
    'TickLength', [0.012 0.012], ...
    'YGrid', 'on', ...
    'XGrid', 'off', ...
    'GridColor', S.grid, ...
    'GridAlpha', 0.92, ...
    'GridLineStyle', '-');
ax.XLabel.FontName = S.font;
ax.XLabel.FontSize = S.axisLabelSize;
ax.XLabel.Color = S.text;
ax.YLabel.FontName = S.font;
ax.YLabel.FontSize = S.axisLabelSize;
ax.YLabel.Color = S.text;
end


function drawHighlights(ax, S, yMin, yMax)
patch(ax, [4.52 5.48 5.48 4.52], [yMin yMin yMax yMax], S.a5bg, ...
    'EdgeColor', 'none', 'HandleVisibility', 'off');
patch(ax, [5.52 6.48 6.48 5.52], [yMin yMin yMax yMax], S.a6bg, ...
    'EdgeColor', 'none', 'HandleVisibility', 'off');
plot(ax, [4.5 4.5], [yMin yMax], '--', 'Color', S.grey, ...
    'LineWidth', 0.52, 'HandleVisibility', 'off');
end


function drawBarOutline(ax, xCenter, baseline, topValue, width, color)
rectangle(ax, 'Position', [xCenter - width / 2, baseline, width, topValue - baseline], ...
    'EdgeColor', color, 'FaceColor', 'none', 'LineWidth', 0.86, ...
    'HandleVisibility', 'off');
end


function belowTitle(ax, panelLetter, titleText, S)
text(ax, 0.5, -0.195, sprintf('\\bf(%s)\\rm  %s', panelLetter, titleText), ...
    'Units', 'normalized', 'Interpreter', 'tex', ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
    'FontName', S.font, 'FontSize', S.titleSize, 'Color', S.text, ...
    'Clipping', 'off');
end


function rgb = hex2rgb(hexColor)
hexColor = char(hexColor);
if hexColor(1) == '#'
    hexColor = hexColor(2:end);
end
rgb = [hex2dec(hexColor(1:2)), hex2dec(hexColor(3:4)), hex2dec(hexColor(5:6))] / 255;
end


function mixed = blendWithWhite(color, strength)
% strength=1 returns the original color; strength=0 returns white.
mixed = 1 - strength * (1 - color);
end


function dataArrow(ax, xTail, yTail, xHead, yHead, xLimits, yLimits, color)
% Draw a predictable arrow in figure-normalized coordinates.
fig = ancestor(ax, 'figure');
pos = ax.Position;
xNorm = pos(1) + ([xTail xHead] - xLimits(1)) ./ diff(xLimits) .* pos(3);
yNorm = pos(2) + ([yTail yHead] - yLimits(1)) ./ diff(yLimits) .* pos(4);
annotation(fig, 'arrow', xNorm, yNorm, ...
    'Color', color, 'LineWidth', 0.62, ...
    'HeadLength', 4.2, 'HeadWidth', 4.2);
end
