import {
  Text,
  View,
  StyleSheet,
  TouchableWithoutFeedback,
  Button,
} from "react-native";
import { MyContext } from "../App";
import { SafeAreaView } from "react-native-safe-area-context";
import { useContext, useEffect, useState } from "react";

const Card = ({ navigation }) => {
  const { state, dispatch } = useContext(MyContext);
  const [isLoad, setLoad] = useState(true);
  const [arr, setArr] = useState([]);

  useEffect(() => {
    setLoad(true);
    const headers = new Headers();
    headers.append("Authorization", `Bearer ${state.token.access_token}`);
    fetch(
      `http://80.78.241.76/api/v1/get_cashback_for_choose/${state.card_id}`,
      {
        method: "GET",
        headers,
      }
    )
      .then((res) => {
        return res.json();
      })
      .then((json) => {
        setLoad(false);
        dispatch({
          type: "SET_CARD",
          payload: json,
        });
      })
      .catch(() => {
        alert("Ошибка");
      });

    return () => {
      setLoad(true);
    };
  }, [state.card_id]);

  useEffect(() => {
    state.card.cashback &&
      setArr(state.card.cashback.slice(0, 3).map((elem) => elem.product_type));

    return () => {
      setArr([]);
    };
  }, [state.card.cashback]);

  const setStyle = (type) => {
    if (arr.includes(type)) return [styles.cashback_total, styles.done];
    return styles.cashback_total;
  };

  const setData = () =>
    arr.reduce(
      (obj, item) => {
        const elem = state.card.cashback.find(
          ({ product_type }) => product_type === item
        );
        if (elem) {
          obj.cashback.push(elem);
        }
        return obj;
      },
      {
        month: "2023-08-29",
        cashback: [],
      }
    );

  return (
    <SafeAreaView style={styles.wrapper}>
      {isLoad ? (
        <Text>Loading...</Text>
      ) : (
        <View style={styles.container}>
          <View style={styles.plastick}>
            <Text style={styles.card_mir}>МИР</Text>
            <Text style={styles.card_name}>{state.card.bank}</Text>
            <Text style={styles.card_numbers}>
              ***{state.card.last_four_digits}
            </Text>
          </View>
          <View style={styles.cashbacks}>
            <Text style={styles.cashbacks_title}>Ваши кешбеки</Text>
            {state.card.cashback.map((elem) => (
              <TouchableWithoutFeedback
                key={elem.product_type}
                onPress={() => {
                  const type = elem.product_type;
                  if (arr.includes(elem.product_type)) {
                    const new_arr = arr.filter((item) => type !== item);
                    setArr(new_arr);
                  } else {
                    if (arr.length < 3) setArr([...arr, type]);
                  }
                }}
              >
                <View style={setStyle(elem.product_type)}>
                  <View style={styles.cashback_type}>
                    <Text>{elem.product_type}:</Text>
                  </View>
                  <View style={styles.cashback_value}>
                    <Text>{elem.value}%</Text>
                  </View>
                </View>
              </TouchableWithoutFeedback>
            ))}
          </View>
          <Button
            style={styles.save}
            onPress={() => {
              fetch(
                `http://80.78.241.76/api/v1/choose_card_cashback/${state.card_id}`,
                {
                  method: "POSt",
                  headers: {
                    Authorization: `Bearer ${state.token.access_token}`,
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify(setData()),
                }
              ).then(() => {
                alert("Кешбеки успешно обнавлены");
                navigation.navigate("Cards");
              });
            }}
            title={arr.length < 3 ? "надо 3 выбрать" : "Сохранить"}
            disabled={arr.length < 3}
          />
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    flex: 1,
  },

  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },

  plastick: {
    position: "relative",
    width: 250,
    height: 120,
    borderWidth: 2,
    borderColor: "green",
    borderRadius: 10,
  },

  card_mir: {
    position: "absolute",
    bottom: 10,
    left: 10,
  },

  card_name: {
    position: "absolute",
    top: 10,
    left: 10,
  },

  done: {
    backgroundColor: "yellow",
  },

  card_numbers: {
    position: "absolute",
    bottom: 10,
    right: 10,
  },

  cashbacks: {
    borderWidth: 2,
    borderColor: "green",
    borderRadius: 5,
    padding: 20,
    minWidth: 250,
  },

  cashbacks_title: {
    color: "blue",
    fontWeight: 500,
    marginBottom: 10,
    textAlign: "center",
    fontSize: 24,
  },

  cashback_total: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 5,
  },

  cashback_type: {
    color: "red",
  },

  cashback_value: {
    color: "green",
  },

  save: {
    padding: 5,
    backgroundColor: "green",
    borderRadius: 5,
    color: "white",
    fontSize: 18,
  },
});

export default Card;
