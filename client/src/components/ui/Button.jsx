
export function Button({ children, variant = 'primary', ...props }) {
    const variants = {
      primary: 'bg-blue-500 text-white hover:bg-blue-600',
      secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
      danger: 'bg-red-500 text-white hover:bg-red-600'
    };
  
    return (
      <button
        className={`px-4 py-2 rounded-md transition-colors ${variants[variant]}`}
        {...props}
      >
        {children}
      </button>
    );
  }
  

