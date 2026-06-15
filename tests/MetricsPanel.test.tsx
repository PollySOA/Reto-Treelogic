/**
 * Tests for MetricsPanel component.
 * 
 * Tests cover:
 * - Metrics display formatting
 * - Compliance indicators
 * - Threshold warnings
 * - Edge cases
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricsPanel from '@/components/MetricsPanel';

describe('MetricsPanel', () => {
  it('renders all metrics', () => {
    const metrics = {
      ssim: 0.9987,
      psnr: 45.32,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/SSIM/i)).toBeDefined();
    expect(screen.getByText(/PSNR/i)).toBeDefined();
    expect(screen.getByText(/Healthy.*Pixels/i)).toBeDefined();
  });

  it('shows AI Act compliance badge for SSIM >= 0.99', () => {
    const metrics = {
      ssim: 0.9987,
      psnr: 45.32,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/AI Act.*Compliant/i)).toBeDefined();
  });

  it('shows warning for SSIM < 0.99', () => {
    const metrics = {
      ssim: 0.9500,
      psnr: 40.00,
      healthy_changed_pixels: 5,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    // Should show warning (not compliance badge)
    const aiActText = screen.queryByText(/AI Act.*Compliant/i);
    expect(aiActText).toBeNull();
  });

  it('formats SSIM with 4 decimal places', () => {
    const metrics = {
      ssim: 0.998765,
      psnr: 45.32,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/0\.9988/)).toBeDefined();
  });

  it('formats PSNR with 2 decimal places', () => {
    const metrics = {
      ssim: 0.9987,
      psnr: 45.3289,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/45\.33/)).toBeDefined();
  });

  it('shows zero healthy pixels changed as success', () => {
    const metrics = {
      ssim: 0.9987,
      psnr: 45.32,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/0/)).toBeDefined();
  });

  it('highlights when healthy pixels are changed', () => {
    const metrics = {
      ssim: 0.9987,
      psnr: 45.32,
      healthy_changed_pixels: 150,
    };

    const { container } = render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/150/)).toBeDefined();
    
    // Should have warning styling
    const warningElements = container.querySelectorAll('[class*="warning"], [class*="destructive"]');
    expect(warningElements.length).toBeGreaterThan(0);
  });

  it('handles edge case with very low SSIM', () => {
    const metrics = {
      ssim: 0.5000,
      psnr: 20.00,
      healthy_changed_pixels: 1000,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/0\.5000/)).toBeDefined();
  });

  it('handles edge case with perfect metrics', () => {
    const metrics = {
      ssim: 1.0000,
      psnr: 100.00,
      healthy_changed_pixels: 0,
    };

    render(<MetricsPanel metrics={metrics} />);
    
    expect(screen.getByText(/1\.0000/)).toBeDefined();
    expect(screen.getByText(/100\.00/)).toBeDefined();
  });
});
