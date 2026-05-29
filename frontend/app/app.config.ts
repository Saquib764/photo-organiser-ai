export default defineAppConfig({
  ui: {
    colors: {
      primary: 'pink',
      secondary: 'indigo',
      neutral: 'gray',
      success: 'emerald',
      info: 'sky',
      warning: 'amber',
      error: 'red',
    },
    notifications: {
      position: 'top-0 bottom-auto',
    },
    button: {
      slots: {
        base: 'cursor-pointer',
      },
      defaultVariants: {
        color: 'primary',
        variant: 'solid',
      },
    },
    input: {
      defaultVariants: {
        size: 'md',
      },
    },
    card: {
      slots: {
        root: 'rounded-lg border border-gray-800 bg-gray-900 shadow-sm hover:border-primary-500/40',
      },
    },
    header: {
      slots: {
        root: 'border-b border-gray-800 bg-gray-900',
      },
    },
    page: {
      slots: {
        root: 'bg-gray-950',
      },
    },
    alert: {
      slots: {
        root: 'rounded-lg',
      },
    },
    tabs: {
      slots: {
        list: 'border-b border-gray-800',
        trigger: 'text-gray-500 data-[state=active]:text-white',
        indicator: 'bg-primary-500',
      },
    },
  },
})
