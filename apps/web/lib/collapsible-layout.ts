"use client";

import { useCallback, useSyncExternalStore } from "react";

const LAYOUT_CHANGE_EVENT = "trading-framework:layout-change";

export function useStoredCollapse(storageKey: string) {
  const subscribe = useCallback((onStoreChange: () => void) => {
    window.addEventListener("storage", onStoreChange);
    window.addEventListener(LAYOUT_CHANGE_EVENT, onStoreChange);
    return () => {
      window.removeEventListener("storage", onStoreChange);
      window.removeEventListener(LAYOUT_CHANGE_EVENT, onStoreChange);
    };
  }, []);
  const getSnapshot = useCallback(
    () => window.localStorage.getItem(storageKey) === "true",
    [storageKey],
  );
  const collapsed = useSyncExternalStore(subscribe, getSnapshot, () => false);

  const toggle = useCallback(() => {
    window.localStorage.setItem(storageKey, String(!getSnapshot()));
    window.dispatchEvent(new Event(LAYOUT_CHANGE_EVENT));
  }, [getSnapshot, storageKey]);

  return [collapsed, toggle] as const;
}

export function useStoredString(storageKey: string, fallback: string) {
  const subscribe = useCallback((onStoreChange: () => void) => {
    window.addEventListener("storage", onStoreChange);
    window.addEventListener(LAYOUT_CHANGE_EVENT, onStoreChange);
    return () => {
      window.removeEventListener("storage", onStoreChange);
      window.removeEventListener(LAYOUT_CHANGE_EVENT, onStoreChange);
    };
  }, []);
  const getSnapshot = useCallback(
    () => window.localStorage.getItem(storageKey) ?? fallback,
    [fallback, storageKey],
  );
  const value = useSyncExternalStore(subscribe, getSnapshot, () => fallback);
  const setValue = useCallback(
    (next: string) => {
      window.localStorage.setItem(storageKey, next);
      window.dispatchEvent(new Event(LAYOUT_CHANGE_EVENT));
    },
    [storageKey],
  );
  return [value, setValue] as const;
}
