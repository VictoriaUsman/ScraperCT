import { Download } from 'lucide-react'
import { getExportUrl } from '@/lib/api'

interface ExportButtonProps {
  type: string
  label?: string
}

export function ExportButton({ type, label }: ExportButtonProps) {
  return (
    <div className="flex items-center gap-2">
      <a
        href={getExportUrl(type, 'csv')}
        download
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
      >
        <Download className="h-3.5 w-3.5" />
        CSV
      </a>
      <a
        href={getExportUrl(type, 'xlsx')}
        download
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
      >
        <Download className="h-3.5 w-3.5" />
        Excel
      </a>
    </div>
  )
}
