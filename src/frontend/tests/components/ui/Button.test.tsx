import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import Button from '../../../src/components/ui/Button'

describe('Button Component', () => {
  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<Button>Default Button</Button>)
      
      const button = screen.getByRole('button', { name: 'Default Button' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('bg-green-500') // primary variant
      expect(button).toHaveClass('py-2') // md size
    })

    it('should render children correctly', () => {
      render(<Button>Click me!</Button>)
      
      expect(screen.getByText('Click me!')).toBeInTheDocument()
    })

    it('should render with custom className', () => {
      render(<Button className="custom-class">Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('custom-class')
    })
  })

  describe('Variants', () => {
    it('should render primary variant correctly', () => {
      render(<Button variant="primary">Primary</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-green-500', 'hover:bg-green-600', 'text-white')
    })

    it('should render secondary variant correctly', () => {
      render(<Button variant="secondary">Secondary</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-gray-200', 'hover:bg-gray-300', 'text-gray-800')
    })

    it('should render danger variant correctly', () => {
      render(<Button variant="danger">Danger</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-red-500', 'hover:bg-red-600', 'text-white')
    })

    it('should render success variant correctly', () => {
      render(<Button variant="success">Success</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('bg-green-500', 'hover:bg-green-600', 'text-white')
    })
  })

  describe('Sizes', () => {
    it('should render small size correctly', () => {
      render(<Button size="sm">Small</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('py-1', 'px-3', 'text-sm', 'rounded')
    })

    it('should render medium size correctly', () => {
      render(<Button size="md">Medium</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('py-2', 'px-4', 'text-base', 'rounded-md')
    })

    it('should render large size correctly', () => {
      render(<Button size="lg">Large</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('py-3', 'px-6', 'text-lg', 'rounded-lg')
    })
  })

  describe('States', () => {
    it('should show loading state correctly', () => {
      render(<Button isLoading>Loading Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      
      // Check for loading indicator (animated dots)
      const loadingDots = button.querySelectorAll('.animate-bounce')
      expect(loadingDots).toHaveLength(3)
    })

    it('should be disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveClass('disabled:opacity-60', 'disabled:cursor-not-allowed')
    })

    it('should render full width correctly', () => {
      render(<Button fullWidth>Full Width</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('w-full')
    })
  })

  describe('Interactions', () => {
    it('should call onClick when clicked', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      
      render(<Button onClick={handleClick}>Click me</Button>)
      
      const button = screen.getByRole('button')
      await user.click(button)
      
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should not call onClick when disabled', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      
      render(<Button onClick={handleClick} disabled>Disabled</Button>)
      
      const button = screen.getByRole('button')
      await user.click(button)
      
      expect(handleClick).not.toHaveBeenCalled()
    })

    it('should not call onClick when loading', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      
      render(<Button onClick={handleClick} isLoading>Loading</Button>)
      
      const button = screen.getByRole('button')
      await user.click(button)
      
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('should have proper focus styles', () => {
      render(<Button>Focusable</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2')
    })

    it('should indicate loading state to screen readers', () => {
      render(<Button isLoading aria-label="Save document">Save</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveAttribute('aria-label', 'Save document')
    })
  })
})
