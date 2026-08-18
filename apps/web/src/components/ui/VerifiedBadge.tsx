import styles from './VerifiedBadge.module.css';

interface VerifiedBadgeProps {
  title?: string;
  className?: string;
}

export default function VerifiedBadge({ title = 'Verified available in India catalog', className = '' }: VerifiedBadgeProps) {
  return (
    <span className={`${styles.badge} ${className}`} title={title}>
      <span className={styles.checkIcon}>&#10003;</span>
      <span>INDIA VERIFIED</span>
    </span>
  );
}
