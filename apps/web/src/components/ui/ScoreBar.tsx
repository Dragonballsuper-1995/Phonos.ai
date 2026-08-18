import styles from './ScoreBar.module.css';

interface ScoreBarProps {
  score: number; // 0 to 100
  isTopRank?: boolean;
  className?: string;
}

export default function ScoreBar({ score, isTopRank = false, className = '' }: ScoreBarProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));

  return (
    <div className={`${styles.track} ${className}`} aria-label={`Score: ${clamped}%`}>
      <div
        className={`${styles.fill} ${isTopRank ? styles.isTopRank : styles.isSecondary}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
