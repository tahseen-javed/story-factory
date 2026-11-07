import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const FACES: Array<[string, string, Record<string, string>?]> = [
  ["Permanent Marker", "fonts/PermanentMarker-Regular.ttf"],
  ["Patrick Hand", "fonts/PatrickHand-Regular.ttf"],
  ["Caveat", "fonts/Caveat-Variable.ttf", { weight: "400 700" }],
  ["Inter", "fonts/Inter-Variable.ttf", { weight: "100 900" }],
  ["Anton", "fonts/Anton-Regular.ttf"],
];

let fontsPromise: Promise<void> | null = null;

function loadAll(): Promise<void> {
  if (!fontsPromise) {
    fontsPromise = Promise.all(
      FACES.map(([name, path, desc]) =>
        new FontFace(name, `url(${staticFile(path)})`, desc as any).load().then((f) => {
          (document as any).fonts.add(f);
        })
      )
    )
      .then(() => undefined)
      .catch((e) => {
        console.error("font load failed", e);
      });
  }
  return fontsPromise;
}

// Loads the self-hosted fonts once per page and holds the render until they are ready.
export function useFonts() {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    loadAll().then(() => continueRender(handle));
  }, [handle]);
}
