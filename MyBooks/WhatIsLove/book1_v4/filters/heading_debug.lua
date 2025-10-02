-- Prefix headings with their level for debugging (e.g., "[H1] Title").
-- Use by setting DEBUG_HEADINGS=1 when running the build.

function Header(el)
  local level = el.level or 0
  local prefix = string.format("[H%d] ", level)
  table.insert(el.content, 1, pandoc.Str(prefix))
  return el
end


