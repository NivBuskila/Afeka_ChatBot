import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import Input from '../../../src/components/ui/Input'

describe('Input Component', () => {
  describe('Rendering', () => {
    it('should render basic input correctly', () => {
      render(<Input placeholder="Enter text" />)
      
      const input = screen.getByPlaceholderText('Enter text')
      expect(input).toBeInTheDocument()
      expect(input).toHaveClass('w-full', 'py-2', 'rounded-md')
    })

    it('should render with label', () => {
      render(<Input label="Email Address" placeholder="email@example.com" />)
      
      expect(screen.getByText('Email Address')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('email@example.com')).toBeInTheDocument()
    })
  })

  describe('Icons', () => {
    it('should render left icon correctly', () => {
      const leftIcon = <span data-testid="left-icon">🔍</span>
      render(<Input leftIcon={leftIcon} />)
      
      expect(screen.getByTestId('left-icon')).toBeInTheDocument()
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('pl-10') // padding for left icon
    })

    it('should handle right icon click', async () => {
      const user = userEvent.setup()
      const handleRightIconClick = vi.fn()
      const rightIcon = <span data-testid="right-icon">👁️</span>
      
      render(
        <Input 
          rightIcon={rightIcon} 
          onRightIconClick={handleRightIconClick}
        />
      )
      
      const rightIconElement = screen.getByTestId('right-icon')
      await user.click(rightIconElement)
      
      expect(handleRightIconClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('Error States', () => {
    it('should display error message', () => {
      render(<Input error="This field is required" />)
      
      expect(screen.getByText('This field is required')).toBeInTheDocument()
      
      const errorText = screen.getByText('This field is required')
      expect(errorText).toHaveClass('text-sm', 'text-red-500', 'mt-1')
    })

    it('should apply error styling to input', () => {
      render(<Input error="Invalid input" />)
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('border-red-500')
    })
  })

  describe('User Interactions', () => {
    it('should handle text input', async () => {
      const user = userEvent.setup()
      const handleChange = vi.fn()
      
      render(<Input onChange={handleChange} />)
      
      const input = screen.getByRole('textbox')
      await user.type(input, 'Hello World')
      
      expect(input).toHaveValue('Hello World')
      expect(handleChange).toHaveBeenCalled()
    })
  })

  describe('Forwarded Ref', () => {
    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLInputElement>()
      
      render(<Input ref={ref} />)
      
      expect(ref.current).toBeInstanceOf(HTMLInputElement)
      expect(ref.current).toBe(screen.getByRole('textbox'))
    })
  })
})