import { useContext, useEffect, useState } from "react";
import {
  Text,
  StyleSheet,
  FlatList,
  View,
  TouchableWithoutFeedback,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { MyContext } from "../App";

const Cards = ({ navigation }) => {
  const { state, dispatch } = useContext(MyContext);
  const [isLoad, setLoad] = useState(false);

  useEffect(() => {
    const headers = new Headers();
    headers.append("Authorization", `Bearer ${state.token.access_token}`);
    fetch("http://80.78.241.76/api/v1/cards", {
      method: "GET",
      headers,
    })
      .then((res) => res.json())
      .then((json) => {
        dispatch({
          type: "SET_CARDS",
          payload: json,
        });
        setLoad(false);
      });

    return () => setLoad(true);
  }, []);

  console.log(state);

  const handleClick = (card_id) => {
    dispatch({
      type: "SET_CARD_ID",
      card_id,
    });
    navigation.navigate("Card");
  };

  const renderItem = ({ item }) => {
    return (
      <TouchableWithoutFeedback
        onPress={() => item.can_choose && handleClick(item.card_id)}
      >
        <View style={styles.card}>
          <View style={styles.card_plastick}>
            <Text style={styles.card_mir}>{item.bank}</Text>
            <Text style={styles.card_numbers}>***{item.last_four_digits}</Text>
          </View>
          <View style={styles.card_cash}>
            <Text style={styles.card_cash_title}>Кешбек</Text>
            {item.cashback.map((elem) => (
              <View style={styles.card_cash_block} key={elem.product_type}>
                <Text>{elem.product_type}:</Text>
                <Text>{elem.value}%</Text>
              </View>
            ))}
            {item.can_choose || (
              <Text style={styles.card_cash_not}>Нельзя менять кешбеки</Text>
            )}
          </View>
        </View>
      </TouchableWithoutFeedback>
    );
  };

  return (
    <SafeAreaView>
      <View style={styles.conatiner}>
        {/* <View style={styles.nav}>
          <TouchableWithoutFeedback>
            <Text>User</Text>
          </TouchableWithoutFeedback>
          <TouchableWithoutFeedback>
            <Text>Mess</Text>
          </TouchableWithoutFeedback>
        </View> */}
        {isLoad ? (
          <Text>Loading...</Text>
        ) : (
          <FlatList
            showsVerticalScrollIndicator={false}
            style={styles.list}
            data={state.cards}
            renderItem={renderItem}
          />
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  conatiner: {
    padding: 10,
  },

  nav: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 20,
  },

  list: {
    padding: 5,
    borderWidth: 2,
    borderColor: "black",
    borderRadius: 20,
  },

  card: {
    padding: 3,
    flexDirection: "row",
    justifyContent: "space-between",
    borderWidth: 2,
    borderColor: "black",
    borderRadius: 5,
    marginBottom: 3,
  },

  card_plastick: {
    position: "relative",
    width: 150,
    height: 70,
    borderWidth: 1,
    borderColor: "green",
    borderRadius: 3,
  },

  card_mir: {
    position: "absolute",
    top: 3,
    left: 3,
  },

  card_numbers: {
    position: "absolute",
    bottom: 3,
    left: 3,
  },

  card_cash: {
    flexDirection: "column",
    alignItems: "flex-end",
  },

  card_cash_block: {
    flexDirection: "row",
    gap: 3,
  },

  card_cash_title: {
    fontWeight: 500,
    marginBottom: 3,
  },

  card_cash_not: {
    color: "red",
    fontWeight: 500,
  },
});

export default Cards;
