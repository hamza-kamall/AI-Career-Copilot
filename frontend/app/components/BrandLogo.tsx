type BrandLogoProps = {
  className?: string;
  compact?: boolean;
  variant?: "default" | "marketing";
};

export function BrandLogo({ className = "", compact = false, variant = "default" }: BrandLogoProps) {
  const src = "/bootcamp-ai-logo-header.png";

  return (
    <span
      className={`brand-logo ${compact ? "brand-logo-compact" : ""} ${className}`}
      aria-label="BootCamp.AI"
      data-variant={variant}
    >
      <img alt="" src={src} />
    </span>
  );
}
