import { Link } from "react-router-dom";
import { ICard, IState } from "../..";
import style from "./Payment.module.scss";
import { FC, useEffect, useState } from "react";

interface ICards {
  cards: ICard[];
}

const Cards: FC<ICards> = ({ cards }) => {
  const [chs_card, setCard] = useState<number>(cards[0].last_four_digits);

  return (
    <div className={style.payment__main}>
      <div className={style.payment__main_cards}>
        {cards.map((item) => (
          <div
            key={item.last_four_digits}
            className={`${style.payment__main_card} ${
              chs_card === item.last_four_digits && style.payment__main_card_chs
            }`}
            onClick={() => setCard(item.last_four_digits)}
          >
            <div className={style.payment__main_card_cashback}>
              Кешбек {!item.cashback && "нет"}
              {!!item.cashback &&
                item.cashback.map(({ product_type, value }) => (
                  <span key={product_type}>
                    {product_type}: {value}%
                  </span>
                ))}
            </div>
            <div className={style.payment__main_card_data}>
              <span className={style.payment__main_card_name}>{item.bank}</span>
              <span className={style.payment__main_card_mir}>МИР</span>
              <span className={style.payment__main_card_numbers}>
                ***{item.last_four_digits}
              </span>
            </div>
          </div>
        ))}
      </div>
      <div className={style.payment__total}>
        <span className={style.payment__total_item}>
          <span>К оплате:</span>
          <span>10000 руб</span>
        </span>
        <span className={style.payment__total_item}>
          <span>Ваш кешбек составит:</span>
          <span>5%</span>
        </span>
      </div>
      <Link to={"/end"} className={style.payment__pay}>
        Оплатить
      </Link>
      <Link to={"/"} className={style.payment__cancel}>
        Отмена
      </Link>
    </div>
  );
};

const Payment: FC<IState> = (props) => {
  const [wellcome, setWellcome] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setWellcome(false);
    }, 2000);

    return () => {
      setWellcome(true);
    };
  }, []);

  return (
    <div className={style.payment}>
      {wellcome ? (
        <div className={style.payment__wellcome}>
          <h1>
            Здравствуйте, {props.name} {props.surname} {props.middlename}
          </h1>
          <button onClick={() => setWellcome(false)}>
            <svg
              width="100px"
              height="100px"
              viewBox="0 0 64 64"
              xmlns="http://www.w3.org/2000/svg"
              xmlnsXlink="http://www.w3.org/1999/xlink"
              aria-hidden="true"
              role="img"
              preserveAspectRatio="xMidYMid meet"
            >
              <circle cx="32" cy="32" r="30" fill="#4bd37b"></circle>
              <path
                fill="#ffffff"
                d="M46 14L25 35.6l-7-7.2l-7 7.2L25 50l28-28.8z"
              ></path>
            </svg>
          </button>
        </div>
      ) : props.cards ? (
        <Cards cards={props.cards} />
      ) : (
        <div className={style.payment__}>У вас нет карт для оплаты</div>
      )}
    </div>
  );
};

export default Payment;
