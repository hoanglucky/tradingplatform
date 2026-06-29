import type { UserSettings } from "@trading-framework/shared";

export type ChartPreferences = {
  symbol: string;
  timeframe: string;
};

export type UserSettingsPatch = Partial<
  Pick<UserSettings, "default_symbol" | "default_timeframe">
>;

export function resolveChartPreferences(
  settings: UserSettings,
  requestedSymbol: string | undefined,
  supportedSymbols: readonly string[],
  supportedTimeframes: readonly string[],
): ChartPreferences {
  const normalizedRequest = requestedSymbol?.trim().toUpperCase();
  const normalizedDefault = settings.default_symbol.trim().toUpperCase();
  const symbol = normalizedRequest && supportedSymbols.includes(normalizedRequest)
    ? normalizedRequest
    : supportedSymbols.includes(normalizedDefault)
      ? normalizedDefault
      : supportedSymbols[0];
  const timeframe = supportedTimeframes.includes(settings.default_timeframe)
    ? settings.default_timeframe
    : supportedTimeframes[0];

  return { symbol, timeframe };
}

async function settingsError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Use the status fallback.
  }
  return `Settings request failed (${response.status}).`;
}

export async function getUserSettings(apiBaseUrl: string, signal?: AbortSignal): Promise<UserSettings> {
  const response = await fetch(`${apiBaseUrl}/settings`, { signal });
  if (!response.ok) {
    throw new Error(await settingsError(response));
  }
  return (await response.json()) as UserSettings;
}

export async function patchUserSettings(
  apiBaseUrl: string,
  patch: UserSettingsPatch,
): Promise<UserSettings> {
  const response = await fetch(`${apiBaseUrl}/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!response.ok) {
    throw new Error(await settingsError(response));
  }
  return (await response.json()) as UserSettings;
}
