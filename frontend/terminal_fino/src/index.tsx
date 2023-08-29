import ReactDOM from "react-dom/client";
import "./styles/index.scss";
import reportWebVitals from "./reportWebVitals";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Main from "./components/main/Main";
import { useReducer } from "react";
import Payment from "./components/payment/Payment";
import End from "./components/end/End";
import LoginError from "./components/login_error/Error";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

interface IProduct {
  product_type: string;
  value: number;
}

export interface ICard {
  bank: string;
  last_four_digits: number;
  cashback: IProduct[] | null;
}

export interface IState {
  status_code?: number;
  name?: string;
  surname?: string;
  middlename?: string;
  cards?: ICard[];
}

export type TypeAction = { type: "SET"; payload: IState };

const reducer = (state: IState, action: TypeAction): IState => {
  switch (action.type) {
    case "SET":
      return { ...action.payload };
    default:
      return state;
  }
};

const App = () => {
  const [state, dispatch] = useReducer(reducer, {});

  return (
    <div className="app">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Main set={dispatch} />} />
          <Route path="/payment" element={<Payment {...state} />} />
          <Route path="/autologin-error" element={<LoginError />} />
          <Route path="/end" element={<End set={dispatch} />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
};

root.render(<App />);

reportWebVitals();
