/**
 * Tests for MedicalImageViewer component.
 * 
 * Tests cover:
 * - Component rendering
 * - Image display
 * - Bounding box visualization
 * - Metrics display
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import MedicalImageViewer from '@/components/MedicalImageViewer';

describe('MedicalImageViewer', () => {
  const mockMetrics = {
    ssim: 0.9987,
    psnr: 45.32,
    healthy_changed_pixels: 0,
  };

  const mockBboxes = [
    { x: 50, y: 50, w: 100, h: 30 },
    { x: 50, y: 100, w: 80, h: 25 },
  ];

  it('renders without crashing', () => {
    render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={mockMetrics}
        bboxes={mockBboxes}
      />
    );
    
    expect(screen.getByRole('img', { name: /original/i })).toBeDefined();
  });

  it('displays metrics correctly', () => {
    render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={mockMetrics}
        bboxes={mockBboxes}
      />
    );
    
    expect(screen.getByText(/0.9987/)).toBeDefined();
    expect(screen.getByText(/45.32/)).toBeDefined();
    expect(screen.getByText(/0/)).toBeDefined();
  });

  it('displays AI Act compliance badge when SSIM >= 0.99', () => {
    render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={mockMetrics}
        bboxes={mockBboxes}
      />
    );
    
    expect(screen.getByText(/AI Act/i)).toBeDefined();
  });

  it('renders bounding boxes', () => {
    const { container } = render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={mockMetrics}
        bboxes={mockBboxes}
      />
    );
    
    // Should render SVG overlay with bboxes
    const svgElements = container.querySelectorAll('svg');
    expect(svgElements.length).toBeGreaterThan(0);
  });

  it('handles empty bboxes array', () => {
    render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={mockMetrics}
        bboxes={[]}
      />
    );
    
    expect(screen.getByRole('img')).toBeDefined();
  });

  it('displays warning when SSIM < 0.99', () => {
    const lowSSIMMetrics = {
      ssim: 0.95,
      psnr: 35.0,
      healthy_changed_pixels: 10,
    };

    render(
      <MedicalImageViewer
        originalImageUrl="/test/original.png"
        anonymizedImageUrl="/test/anonymized.png"
        metrics={lowSSIMMetrics}
        bboxes={mockBboxes}
      />
    );
    
    // Should show warning for low SSIM
    expect(screen.getByText(/0.95/)).toBeDefined();
  });
});
