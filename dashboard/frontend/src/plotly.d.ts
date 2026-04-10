declare module "react-plotly.js" {
  import { Component } from "react";

  interface PlotParams {
    data: Plotly.Data[];
    layout?: Partial<Plotly.Layout>;
    config?: Partial<Plotly.Config>;
    frames?: Plotly.Frame[];
    style?: React.CSSProperties;
    className?: string;
    onInitialized?: (figure: Readonly<{ data: Plotly.Data[]; layout: Partial<Plotly.Layout> }>, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: Readonly<{ data: Plotly.Data[]; layout: Partial<Plotly.Layout> }>, graphDiv: HTMLElement) => void;
    onPurge?: (figure: Readonly<{ data: Plotly.Data[]; layout: Partial<Plotly.Layout> }>, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    useResizeHandler?: boolean;
  }

  export default class Plot extends Component<PlotParams> {}
}

declare namespace Plotly {
  interface Data {
    x?: (number | string)[];
    y?: (number | string)[];
    z?: (number | string)[];
    mode?: string;
    type?: string;
    name?: string;
    text?: string | string[];
    hoverinfo?: string;
    marker?: Partial<{
      color: string | string[] | number[];
      colorscale: string | [number, string][];
      size: number | number[];
      opacity: number;
      colorbar: Partial<{ title: string; thickness: number }>;
    }>;
    boxpoints?: boolean | string;
    [key: string]: unknown;
  }

  interface Layout {
    width?: number;
    height?: number;
    title?: string;
    xaxis?: Partial<{ title: string; zeroline: boolean }>;
    yaxis?: Partial<{ title: string; zeroline: boolean; range: number[] }>;
    legend?: Partial<{ orientation: string; x: number; y: number; font: Partial<{ size: number }> }>;
    margin?: Partial<{ t: number; l: number; r: number; b: number }>;
    paper_bgcolor?: string;
    plot_bgcolor?: string;
    barmode?: string;
    showlegend?: boolean;
    shapes?: Shape[];
    [key: string]: unknown;
  }

  interface Shape {
    type?: string;
    x0?: number;
    x1?: number;
    y0?: number;
    y1?: number;
    xref?: string;
    yref?: string;
    line?: Partial<{ dash: string; color: string; width: number }>;
  }

  interface Config {
    responsive?: boolean;
    displayModeBar?: boolean;
    [key: string]: unknown;
  }

  interface Frame {
    name?: string;
    data?: Data[];
    layout?: Partial<Layout>;
  }
}
