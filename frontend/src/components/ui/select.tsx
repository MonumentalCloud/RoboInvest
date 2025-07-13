import * as React from "react"

export interface SelectProps {
  value?: string
  onValueChange?: (value: any) => void
  children: React.ReactNode
}

export interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
}

export interface SelectContentProps {
  children: React.ReactNode
}

export interface SelectItemProps {
  value: string
  children: React.ReactNode
}

const Select = ({ value, onValueChange, children }: SelectProps) => {
  return <div className="relative">{children}</div>
}

const SelectTrigger = React.forwardRef<HTMLButtonElement, SelectTriggerProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
        {...props}
      >
        {children}
        <svg
          className="h-4 w-4 opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
    )
  }
)
SelectTrigger.displayName = "SelectTrigger"

const SelectContent = ({ children }: SelectContentProps) => {
  return (
    <div className="absolute top-full z-50 mt-1 w-full rounded-md border border-gray-300 bg-white shadow-lg">
      {children}
    </div>
  )
}

const SelectItem = ({ value, children }: SelectItemProps) => {
  return (
    <div className="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-gray-100 focus:bg-gray-100">
      {children}
    </div>
  )
}

const SelectValue = ({ placeholder }: { placeholder?: string }) => {
  return <span className="text-gray-900">{placeholder}</span>
}

export { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } 