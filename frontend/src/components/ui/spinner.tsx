import * as React from "react"
import { cn } from "@/lib/utils"

const Spinner = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      role="status"
      className={cn("animate-spin rounded-full border-2 border-current border-t-transparent", className)}
      {...props}
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
)
Spinner.displayName = "Spinner"

export { Spinner }
