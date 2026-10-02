import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router'

import { AppHeader } from '@/components/AppHeader'
import { ROUTE_PATHS } from '@/consts'
import { HomePage } from '@/pages/HomePage/HomePage'
import { RunPage } from '@/pages/RunPage/RunPage'

const QUERY_RETRY_COUNT = 1
const ANY_PATH = '*'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: QUERY_RETRY_COUNT, refetchOnWindowFocus: false } },
})

function AppLayout() {
  const location = useLocation()
  return (
    <>
      <AppHeader showNewScene={location.pathname !== ROUTE_PATHS.HOME} />
      <Routes>
        <Route path={ROUTE_PATHS.HOME} element={<HomePage />} />
        <Route path={ROUTE_PATHS.RUN} element={<RunPage />} />
        <Route path={ANY_PATH} element={<Navigate to={ROUTE_PATHS.HOME} replace />} />
      </Routes>
    </>
  )
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
