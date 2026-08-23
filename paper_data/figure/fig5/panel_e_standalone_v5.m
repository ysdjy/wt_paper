% Panel (e) v5 standalone: confidence trajectory rendered as a genuine 3D TUBE (not a flat
% ribbon) -- centerline = real (relative_life, q_pred, max_prob); tube cross-section radius at
% each point is driven by that run's real `uncertainty` (normalized), a visual ENCODING only
% (documented: no physical q-magnitude meaning). Tube built via a stable parallel-transport-style
% frame computed in per-axis-normalized space (so the tube reads as round/tube-like despite the
% three axes having different physical units/ranges -- standard practice for streamtube-style
% plots over non-isotropic data). Surface color = real max_prob. PCHIP interpolation (304->800)
% is display-resolution only; real 304-run markers plotted on the centerline.
function panel_e_standalone_v5()
close all;
here = fileparts(mfilename('fullpath'));
conf_t = readtable(fullfile(here, 'derived', 'confidence_ribbon_v4.csv'));
assert(height(conf_t) == 304, 'confidence_ribbon_v4.csv must have 304 real rows');

[life, ord] = sort(conf_t.relative_life);
qpred = conf_t.q_pred(ord);
maxp  = conf_t.max_prob(ord);
unc   = conf_t.uncertainty(ord);

N_DISP = 800;
xq = linspace(min(life), max(life), N_DISP)';
yq = pchip(life, qpred, xq);
zq = pchip(life, maxp,  xq);
uq = pchip(life, unc,   xq);
uq = max(uq, 0);  % pchip can slightly overshoot near sharp real transitions; radius must stay >=0

% ---- real uncertainty -> tube half-width (visual encoding only, no physical q-meaning) ----
u_norm = (uq - min(uq)) / (max(uq) - min(uq) + eps);
W_MIN = 0.012; W_MAX = 0.075;
radius = W_MIN + u_norm * (W_MAX - W_MIN);

% ---- build tube geometry in per-axis-NORMALIZED space, then map back to real data units ----
rangeX = max(xq)-min(xq); rangeY = max(yq)-min(yq); rangeZ = max(zq)-min(zq);
xn = xq/rangeX; yn = yq/rangeY; zn = zq/rangeZ;
C = [xn, yn, zn];  % Nx3 normalized centerline

N = size(C,1);
T = zeros(N,3);
T(2:end-1,:) = C(3:end,:) - C(1:end-2,:);
T(1,:) = C(2,:) - C(1,:);
T(end,:) = C(end,:) - C(end-1,:);
T = T ./ vecnorm(T,2,2);

% simple stable frame: pick a reference vector not parallel to T, project out T, normalize;
% propagate frame along the curve (parallel transport) to avoid twisting/flipping.
ref = [0 0 1];
N1 = zeros(N,3); B1 = zeros(N,3);
v0 = ref - dot(ref, T(1,:))*T(1,:);
if norm(v0) < 1e-6; ref = [0 1 0]; v0 = ref - dot(ref,T(1,:))*T(1,:); end
N1(1,:) = v0 / norm(v0);
B1(1,:) = cross(T(1,:), N1(1,:));
for i = 2:N
    % rotate previous normal to be orthogonal to the new tangent (minimal rotation / parallel transport)
    v = N1(i-1,:) - dot(N1(i-1,:), T(i,:))*T(i,:);
    if norm(v) < 1e-8
        v = B1(i-1,:) - dot(B1(i-1,:), T(i,:))*T(i,:);
    end
    N1(i,:) = v / norm(v);
    B1(i,:) = cross(T(i,:), N1(i,:));
end

M = 18;  % points around the tube circumference
theta = linspace(0, 2*pi, M);
Xt = zeros(N,M); Yt = zeros(N,M); Zt = zeros(N,M); Ct_color = zeros(N,M);
for i = 1:N
    circ = radius(i) * (cos(theta)'*N1(i,:) + sin(theta)'*B1(i,:));  % Mx3, in normalized space
    pts_n = C(i,:) + circ;  % Mx3 normalized
    Xt(i,:) = pts_n(:,1)'*rangeX;
    Yt(i,:) = pts_n(:,2)'*rangeY;
    Zt(i,:) = pts_n(:,3)'*rangeZ;
    Ct_color(i,:) = zq(i);  % face color = real max_prob at this point (constant around circumference)
end

angles_to_try = [-52 25; -40 20; -60 30; -35 35; -65 18];
for a = 1:size(angles_to_try,1)
    fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 6.5 5.2]);
    ax = axes(fig); hold(ax,'on');

    % floor projection of the real (relative_life, q_pred) trajectory, colored by real max_prob
    plot3(ax, xq, yq, zeros(size(xq)), '-', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.6);
    % a handful of real vertical stems from floor to the centerline (every ~27 runs)
    stem_idx = 1:27:N_DISP;
    for si = stem_idx
        plot3(ax, [xq(si) xq(si)], [yq(si) yq(si)], [0 zq(si)], '-', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.6);
    end

    surf(ax, Xt, Yt, Zt, Ct_color, 'EdgeColor','none', 'FaceLighting','gouraud', ...
         'AmbientStrength',0.32, 'DiffuseStrength',0.75, 'SpecularStrength',0.25, 'SpecularExponent', 12);
    colormap(ax, turbo);
    clim_lo = min(maxp); clim_hi = max(maxp);
    caxis(ax, [clim_lo clim_hi]);

    % real centerline highlight + real run markers every ~18 runs
    plot3(ax, xq, yq, zq, 'Color', [1 1 1], 'LineWidth', 1.8);
    mk_idx = 1:18:length(life);
    plot3(ax, life(mk_idx), qpred(mk_idx), maxp(mk_idx), 'o', ...
          'MarkerFaceColor', [1 1 1], 'MarkerEdgeColor', [0.15 0.15 0.15], 'MarkerSize', 3.4, 'LineWidth', 0.6);

    set(ax,'Color','none');
    grid(ax,'on'); ax.GridAlpha = 0.14; ax.GridColor = [0.6 0.6 0.6];
    box(ax,'off');
    xlabel(ax,'Relative life','FontName','Times New Roman','FontSize',10);
    ylabel(ax,'q_{pred} (raw)','FontName','Times New Roman','FontSize',10);
    zlabel(ax,'Max probability (confidence)','FontName','Times New Roman','FontSize',10);
    zlim(ax,[0 1]);
    pbaspect(ax, [1.7 1.0 0.95]);
    camproj(ax,'perspective');
    view(ax, angles_to_try(a,1), angles_to_try(a,2));
    camlight(ax,'headlight');
    camlight(ax,'left');
    lighting(ax,'gouraud');
    material(ax,'dull');
    set(ax,'FontName','Times New Roman');
    cb = colorbar(ax); cb.Label.String = 'max probability (confidence)'; cb.FontName='Times New Roman'; cb.FontSize=8;

    outp = fullfile(here, 'outputs', 'panel_e_camera_trials', sprintf('angle_%d_az%d_el%d.png', a, angles_to_try(a,1), angles_to_try(a,2)));
    if ~exist(fileparts(outp),'dir'); mkdir(fileparts(outp)); end
    exportgraphics(fig, outp, 'Resolution', 200);
    close(fig);
    fprintf('Rendered %s\n', outp);
end
fprintf('panel_e_standalone_v5 done.\n');
end
