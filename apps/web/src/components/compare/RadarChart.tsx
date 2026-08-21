'use client';

import React, { useState } from 'react';
import type { PhoneDetails } from '@/lib/types';
import { cleanPhoneName, compute5DVector, type HardwareVector5D } from '@/lib/specHelpers';
import styles from './RadarChart.module.css';

interface RadarChartProps {
  phones: PhoneDetails[];
}

export const PALETTE = [
  { stroke: '#00E599', fill: 'rgba(0, 229, 153, 0.16)', dot: '#00E599', marker: 'circle' },  // Neon Emerald
  { stroke: '#8B5CF6', fill: 'rgba(139, 92, 246, 0.16)', dot: '#8B5CF6', marker: 'square' },  // Electric Purple
  { stroke: '#FF6B00', fill: 'rgba(255, 107, 0, 0.16)', dot: '#FF6B00', marker: 'diamond' },  // Flame Amber
  { stroke: '#00B4D8', fill: 'rgba(0, 180, 216, 0.16)', dot: '#00B4D8', marker: 'triangle' }, // Sky Cyan
  { stroke: '#EC4899', fill: 'rgba(236, 72, 153, 0.16)', dot: '#EC4899', marker: 'cross' },   // Rose Fuchsia
];

const AXES: Array<{ key: keyof HardwareVector5D; label: string; angle: number }> = [
  { key: 'performance', label: 'PERFORMANCE', angle: -90 },  // Top (0 deg offset)
  { key: 'camera', label: 'CAMERAS / OPTICS', angle: -18 },  // Top-Right
  { key: 'display', label: 'DISPLAY QUALITY', angle: 54 },   // Bottom-Right
  { key: 'battery', label: 'BATTERY & CHARGING', angle: 126 },// Bottom-Left
  { key: 'build', label: 'BUILD / DURABILITY', angle: 198 }, // Top-Left
];

export default function RadarChart({ phones }: RadarChartProps) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  if (!phones || phones.length === 0) return null;

  const size = 420;
  const center = size / 2;
  const radius = 135;
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];

  // Helper to calculate (x, y) for a given angle & normalized value (0-1)
  const getCoordinates = (angleDeg: number, valueNorm: number) => {
    const angleRad = (angleDeg * Math.PI) / 180;
    const r = radius * valueNorm;
    return {
      x: center + r * Math.cos(angleRad),
      y: center + r * Math.sin(angleRad),
    };
  };

  // Compute 5D vectors for each phone
  const phoneVectors = phones.slice(0, 5).map((phone, idx) => ({
    phone,
    idx,
    vector: compute5DVector(phone),
  }));

  return (
    <div className={styles.container} aria-label="5D Hardware Benchmark Radar Chart">
      <div className={styles.header}>
        <div className={styles.headerTitleGroup}>
          <span className={styles.badge}>SCIENTIFIC 5D MATRIX</span>
          <h2 className={styles.title}>5D HARDWARE BENCHMARK RADAR</h2>
        </div>
        <span className={styles.subtitle}>DXOMARK • GEEKBENCH 6 • VCX FORUM • GSMARENA FUSION</span>
      </div>

      <div className={styles.chartWrapper}>
        <svg viewBox={`0 0 ${size} ${size}`} className={styles.svg}>
          {/* Concentric Pentagon Background Bands & Grid Lines */}
          {levels.map((lvl, idx) => {
            const points = AXES.map((axis) => {
              const { x, y } = getCoordinates(axis.angle, lvl);
              return `${x},${y}`;
            }).join(' ');

            return (
              <g key={idx}>
                {/* Concentric Pentagon Ring */}
                <polygon
                  points={points}
                  className={styles.gridPolygon}
                  fill={idx % 2 === 0 ? 'var(--color-radar-band, rgba(0,0,0,0.02))' : 'transparent'}
                />
                <polygon
                  points={points}
                  className={styles.gridLine}
                />
              </g>
            );
          })}

          {/* Radial Axis Guide Rays */}
          {AXES.map((axis, idx) => {
            const endCoord = getCoordinates(axis.angle, 1.0);
            const labelCoord = getCoordinates(axis.angle, 1.28);

            return (
              <g key={idx}>
                {/* Radial Ray */}
                <line
                  x1={center}
                  y1={center}
                  x2={endCoord.x}
                  y2={endCoord.y}
                  className={styles.axisRay}
                />
                {/* Axis Name Label */}
                <text
                  x={labelCoord.x}
                  y={labelCoord.y}
                  className={styles.axisLabel}
                >
                  {axis.label}
                </text>
              </g>
            );
          })}

          {/* Percentage Scale Labels along the Top Ray */}
          {levels.map((lvl, idx) => {
            const coord = getCoordinates(-90, lvl);
            return (
              <text
                key={`lvl-${idx}`}
                x={coord.x + 8}
                y={coord.y + 3}
                className={styles.scaleLabel}
              >
                {Math.round(lvl * 100)}%
              </text>
            );
          })}

          {/* Center Point */}
          <circle cx={center} cy={center} r={3} className={styles.centerDot} />

          {/* Phone Hardware Polygons */}
          {phoneVectors.map(({ vector, idx }) => {
            const color = PALETTE[idx % PALETTE.length];
            const isHovered = hoveredIdx === idx;
            const isDimmed = hoveredIdx !== null && hoveredIdx !== idx;

            const points = AXES.map((axis) => {
              const score = vector[axis.key] || 50;
              const { x, y } = getCoordinates(axis.angle, score / 100);
              return `${x},${y}`;
            }).join(' ');

            return (
              <g
                key={idx}
                className={styles.phoneGroup}
                style={{
                  opacity: isDimmed ? 0.25 : 1.0,
                  transition: 'opacity 0.25s ease',
                }}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                <polygon
                  points={points}
                  fill={color.fill}
                  stroke={color.stroke}
                  strokeWidth={isHovered ? 3.2 : 2.2}
                  className={styles.polygon}
                />

                {/* Distinct Vertex Markers */}
                {AXES.map((axis, aIdx) => {
                  const score = vector[axis.key] || 50;
                  const { x, y } = getCoordinates(axis.angle, score / 100);
                  const radiusOffset = 3.5 + (idx * 0.8);

                  return (
                    <g key={aIdx}>
                      <circle
                        cx={x}
                        cy={y}
                        r={isHovered ? radiusOffset + 2 : radiusOffset}
                        fill={color.stroke}
                        stroke="var(--color-surface, #FFF)"
                        strokeWidth={1.5}
                        className={styles.vertexDot}
                      />
                    </g>
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend with interactive hover & rankings */}
      <div className={styles.legend}>
        {(() => {
          // Compute true ranks based on composite score
          const sortedByScore = [...phoneVectors]
            .map((pv) => ({
              ...pv,
              avg: (pv.vector.performance + pv.vector.camera + pv.vector.display + pv.vector.battery + pv.vector.build) / 5,
            }))
            .sort((a, b) => b.avg - a.avg);

          const rankMap = new Map<number | string, number>();
          sortedByScore.forEach((item, rIdx) => {
            rankMap.set(item.phone.id || item.idx, rIdx + 1);
          });

          return phoneVectors.map(({ phone, vector, idx }) => {
            const color = PALETTE[idx % PALETTE.length];
            const name = cleanPhoneName(phone.fullName || phone.name || '', phone.brand || '');
            const avgScore = Math.round(
              (vector.performance + vector.camera + vector.display + vector.battery + vector.build) / 5
            );
            const isHovered = hoveredIdx === idx;
            const rank = rankMap.get(phone.id || idx) || (idx + 1);

            return (
              <div
                key={phone.id || idx}
                className={`${styles.legendItem} ${isHovered ? styles.legendItemActive : ''}`}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                <span
                  className={styles.colorDot}
                  style={{ backgroundColor: color.stroke }}
                />
                <span className={styles.legendRank}>#{rank}</span>
                <span className={styles.legendName}>{phone.brand} {name}</span>
                <span className={styles.legendScore}>{avgScore}/100</span>
              </div>
            );
          });
        })()}
      </div>
    </div>
  );
}
