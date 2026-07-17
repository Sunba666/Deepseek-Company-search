export interface SEOMeta {
  title: string;
  description: string;
  ogImage?: string;
  canonical?: string;
  jsonLd?: Record<string, unknown>;
}

const BASE_URL = "https://jobnav.ai";

export function buildMetadata(meta: SEOMeta) {
  return {
    title: meta.title,
    description: meta.description,
    openGraph: {
      title: meta.title,
      description: meta.description,
      url: meta.canonical ? BASE_URL + meta.canonical : BASE_URL,
      siteName: "JobNav AI",
      locale: "zh_CN",
      type: "website" as const,
    },
    twitter: {
      card: "summary_large_image" as const,
      title: meta.title,
      description: meta.description,
    },
    alternates: meta.canonical ? { canonical: BASE_URL + meta.canonical } : undefined,
  };
}
